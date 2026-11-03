/* Destructive workflow checks are allowed only against the caller's isolated test project. */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const root=path.resolve(__dirname,'..'),fixture=path.resolve(process.argv[3]||'.'),url=process.argv[2];
if(!fixture.startsWith(path.join(root,'build','tests','ed-'))||!url||new URL(url).port==='8765')throw Error('An isolated ed-* fixture server is required');
const {chromium}=require(process.env.LEAGUE_ANKI_PLAYWRIGHT||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
(async()=>{
 const candidates=[process.env.LEAGUE_ANKI_BROWSER,'C:/Program Files/Microsoft/Edge/Application/msedge.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe',chromium.executablePath()].filter(Boolean);
 const executablePath=candidates.find(p=>fs.existsSync(p));
 if(!executablePath)throw Error('Set LEAGUE_ANKI_BROWSER to an installed Chromium browser');
 const browser=await chromium.launch({headless:true,executablePath});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[],actions=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(r.method()==='POST')actions.push(r.postDataJSON().action)});
  await page.goto(url);await page.selectOption('#champion','Braum');
  await page.locator('#propose').click();
  await page.locator('#proposalConfirm').waitFor();
  if(!(await page.locator('#proposalResult').innerText()).includes('100 → 106 approved cards'))throw Error('Readable counts are missing');
  if(!(await page.locator('#proposalResult').innerText()).includes('Concussive Blows'))throw Error('Proposed cards are missing');
  if(!await page.locator('#applyProposal').isDisabled())throw Error('Apply enabled before confirmation/name');
  await page.locator('#proposalConfirm').check();
  if(!await page.locator('#applyProposal').isDisabled())throw Error('Reviewer name must be required');
  await page.locator('#proposalReviewer').fill('Isolated browser reviewer');
  await page.locator('#applyProposal').click();
  await page.locator('#buildEditorial').waitFor();
  await page.waitForFunction(()=>!document.querySelector('#buildEditorial').disabled);
  await page.locator('#buildEditorial').click();
  await page.locator('#downloadApkg').waitFor({timeout:120000});
  if(!(await page.locator('#proposalResult').innerText()).includes('106 cards · 106 notes'))throw Error('Build summary missing counts');
  const pending=page.waitForEvent('download');await page.locator('#downloadApkg').click();const download=await pending;
  const destination=path.join(fixture,'build','browser-downloaded.apkg');await download.saveAs(destination);
  if(fs.statSync(destination).size<100000)throw Error('APKG download was empty');
  if(actions.join(',')!=='propose,apply-proposal,build-editorial')throw Error('Unexpected duplicate/action sequence: '+actions);
  if(errors.length)throw Error(errors.join('\n'));
  await page.screenshot({path:path.join(root,'build/ui-export/browser-workflow.png'),fullPage:false});
  fs.writeFileSync(path.join(root,'build/ui-export/browser-checks.json'),JSON.stringify({passed:true,actions,approved_cards:106,blank_notes:true,download:true,live_mutations:0},null,2)+'\n');
  process.stdout.write('Isolated browser proposal → inspect → apply → build → download passed.\n');
 }finally{await browser.close()}
})().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1});
