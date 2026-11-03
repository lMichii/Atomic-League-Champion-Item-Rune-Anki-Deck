/* Browser-to-HTTP review check against an isolated editorial fixture. */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),readline=require('node:readline');
const {spawn}=require('node:child_process');
const {chromium}=require(process.env.LEAGUE_ANKI_PLAYWRIGHT||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
const root=path.resolve(__dirname,'..');
const python=`import sys,threading\nsys.path[:0]=[r'${root.replaceAll('\\','\\\\')}',r'${path.join(root,'tests').replaceAll('\\','\\\\')}']\nfrom test_editorial import EditorialTests\nfrom lol_anki.editorial_server import make_server\nfixture=EditorialTests('test_combined_approval_is_atomic_and_records_both_decisions')\nfixture.setUp()\nserver=make_server(fixture.root,0)\nthread=threading.Thread(target=server.serve_forever,daemon=True)\nthread.start()\nprint(f'http://127.0.0.1:{server.server_port}',flush=True)\ninput()\nserver.shutdown();server.server_close();thread.join();fixture.tearDown()\n`;
(async()=>{
 const child=spawn('python',['-c',python],{cwd:root,stdio:['pipe','pipe','inherit']});
 let browser;
 try{
  const lines=readline.createInterface({input:child.stdout});
  const url=await Promise.race([new Promise((resolve,reject)=>{lines.once('line',resolve);child.once('exit',code=>reject(Error('Fixture server exited: '+code)))}),new Promise((_,reject)=>setTimeout(()=>reject(Error('Fixture server timed out')),30000))]);
  const candidates=[process.env.LEAGUE_ANKI_BROWSER,'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe',chromium.executablePath()].filter(Boolean);
  const executablePath=candidates.find(fs.existsSync);
  if(!executablePath)throw Error('No local Chromium browser found');
  browser=await chromium.launch({headless:true,executablePath});
  const page=await browser.newPage(),posts=[];
  page.on('request',request=>{if(request.url().endsWith('/api/action'))posts.push(request.postDataJSON())});
  await page.goto(url);
  const initial=await (await page.request.get(url+'/api/state')).json();
  const card=initial.cards.find(c=>c.id==='champ:201:q:recognize:L2');
  if(!card)throw Error('Isolated Braum Q card missing');
  await page.selectOption('#champion','Braum');
  await page.locator('#list button').filter({hasText:'Q · '+card.working.row.ability}).first().click();
  await page.locator('#reviewer').fill('Browser fixture reviewer');
  await page.locator('#combinedApprove').click();
  if(posts.length||!((await page.locator('#message').innerText()).includes('confirm both')))throw Error('Missing confirmation was submitted');
  await page.locator('#combinedConfirm').check();
  await page.locator('[data-source]').first().check();
  await page.locator('#combinedApprove').click();
  await page.waitForFunction(()=>document.querySelector('#reviewStatus')?.textContent.includes('Content: approved · Media: approved'));
  if(posts.length!==1||posts[0].action!=='approve-content-and-media'||posts[0].notes!=='')throw Error('Browser sent the wrong combined action or required notes');
  const state=await (await page.request.get(url+'/api/state')).json();
  const saved=state.cards.find(c=>c.id===card.id);
  if(saved.content_review.status!=='approved'||saved.media_review.status!=='approved')throw Error('Both approval statuses were not refreshed from the HTTP server');
  process.stdout.write('Isolated browser click reached the HTTP combined action and refreshed both approval statuses.\n');
 }finally{
  if(browser)await browser.close();
  child.stdin.end('\n');
  await new Promise(resolve=>{if(child.exitCode!==null)resolve();else child.once('exit',resolve)});
 }
})().catch(error=>{process.stderr.write(error.stack+'\n');process.exitCode=1});
