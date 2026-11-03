/* Read-only browser verification of batch drafts in the existing review service. */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const root=path.resolve(__dirname,'..'),batch=process.argv[2],base=process.argv[3]||'http://127.0.0.1:8765';
if(!/^[a-z0-9][a-z0-9_-]{0,70}$/.test(batch||''))throw Error('Supply a saved batch ID');
const {chromium}=require(process.env.LEAGUE_ANKI_PLAYWRIGHT||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
(async()=>{
 const candidates=[process.env.LEAGUE_ANKI_BROWSER,'C:/Program Files/Microsoft/Edge/Application/msedge.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe',chromium.executablePath()].filter(Boolean);
 const browser=await chromium.launch({headless:true,executablePath:candidates.find(p=>fs.existsSync(p))});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1050}}),errors=[],posts=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',async route=>{if(route.request().method()==='POST'){posts.push(route.request().url());return route.abort()}return route.continue()});
  await page.goto(base);await page.waitForSelector('#list button');
  const state=await (await page.request.get(new URL('/api/state',base).href)).json();
  const list=JSON.parse(fs.readFileSync(path.join(root,'data/batches',batch,'cards.json'),'utf8')).cards.filter(c=>c.status==='pending_editorial_review');
  let checked=0;const champions=new Set();
  for(const draft of list){
   const c=state.cards.find(c=>c.id===draft.id);if(!c)throw Error('Draft missing from editorial registry: '+draft.id);
   await page.selectOption('#champion',c.champion);
   await page.locator('#list button').filter({hasText:c.working.row.slot+' · '+c.working.row.ability}).first().click();
   const frame=page.frameLocator('iframe');await frame.locator('#front').waitFor();
   await frame.locator('body').evaluate(()=>new Promise((resolve,reject)=>{let count=0;function poll(){if([...document.images].every(i=>i.complete&&i.naturalWidth>0))return resolve();if(++count>100)return reject(Error('Image did not decode'));setTimeout(poll,50)}poll()}));
   await frame.getByRole('button').click();const text=await frame.locator('#back').innerText();
   if(!text.includes('Counterplay:')||/\b(INFERRED|UNVERIFIED|SUPPORTED|confidence|Patch)\b/i.test(text))throw Error('Learning/QA separation failed: '+draft.id);
   if(await page.locator('#answer').inputValue()!==c.working.row.answer)throw Error('Editorial answer mismatch: '+draft.id);
   checked++;champions.add(c.champion);
  }
  if(posts.length||errors.length)throw Error(JSON.stringify({posts,errors}));
  const folder=path.join(root,'build/batch-pilot');fs.mkdirSync(folder,{recursive:true});
  await page.screenshot({path:path.join(folder,'editorial-preview.png'),fullPage:false});
  fs.writeFileSync(path.join(folder,'browser-checks.json'),JSON.stringify({batch,passed:true,cards:checked,champions:[...champions],post_requests:posts.length},null,2)+'\n');
  process.stdout.write(`Verified ${checked} drafts across ${champions.size} champions; no review mutations.\n`);
 }finally{await browser.close()}
})().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1});
