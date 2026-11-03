/* Browser checks use an in-memory state fixture; no review writes reach the workspace. */
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..');
const {chromium}=require(process.env.LEAGUE_ANKI_PLAYWRIGHT||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'));
(async()=>{
 const candidates=[process.env.LEAGUE_ANKI_BROWSER,'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',chromium.executablePath()].filter(Boolean);
 const executablePath=candidates.find(p=>fs.existsSync(p));
 if(!executablePath)throw Error('Set LEAGUE_ANKI_BROWSER to an installed local Chromium browser.');
 const browser=await chromium.launch({headless:true,executablePath});
 try{
  const page=await browser.newPage({viewport:{width:1450,height:1050}}),posts=[],postBodies=[];
  page.on('request',r=>{if(r.method()==='POST')posts.push(r.url())});
  page.on('pageerror',e=>process.stderr.write('Browser page error: '+e.message+' '+e.stack+'\n'));
  const offlineState=process.env.LEAGUE_ANKI_STATE_FILE?JSON.parse(fs.readFileSync(process.env.LEAGUE_ANKI_STATE_FILE,'utf8')):null;
  if(offlineState){
   const html=fs.readFileSync(path.join(root,'lol_anki/editorial_ui.html'),'utf8').replaceAll('__NONCE__','offline-test-token');
   await page.route('http://127.0.0.1:8765/**',async route=>{
    const pathname=new URL(route.request().url()).pathname;
    if(pathname==='/')return route.fulfill({status:200,contentType:'text/html',body:html});
    if(pathname==='/editorial-export.js')return route.fulfill({status:200,contentType:'text/javascript',body:fs.readFileSync(path.join(root,'lol_anki/editorial_export_ui.js'),'utf8')});
    if(pathname==='/api/workflow')return route.fulfill({status:200,contentType:'application/json',body:'{"proposals":[]}'});
    if(pathname==='/api/state')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(offlineState)});
    if(pathname==='/api/action'&&route.request().method()==='POST'){
     const body=route.request().postDataJSON();postBodies.push(body);
     const card=offlineState.cards.find(x=>x.id===body.id);
     if(body.action==='approve-content-and-media'&&card){card.content_review={...card.content_review,status:'approved',reviewer:body.reviewer,notes:body.notes,selected_source_ids:body.source_ids};card.media_review={...card.media_review,status:'approved',reviewer:body.reviewer,notes:body.notes,media_sha256:card.media.signature,media_file_hashes:card.media.files};card.revision++}
     return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({result:{ok:true}})});
    }
    if(pathname.startsWith('/preview/'))return route.fulfill({status:200,contentType:'text/html',body:'<!doctype html><p>Preview fixture</p>'});
    return route.fulfill({status:404,body:'Not found'});
   });
   await page.goto('http://127.0.0.1:8765');
  }else await page.goto(process.argv[2]||'http://127.0.0.1:8765');
  await page.waitForTimeout(1000);
  if(!await page.locator('#list button').count())throw Error('Review UI did not render cards: '+(await page.locator('#message').innerText()));
  const state=offlineState||await (await page.request.get(new URL('/api/state',page.url()).href)).json();let checked=0;
  for(const c of offlineState?[]:state.cards){
   await page.selectOption('#champion',c.champion);
   await page.locator('#list button').filter({hasText:c.working.row.slot+' · '+c.working.row.ability}).first().click();
   const frame=page.frameLocator('iframe');
   await frame.locator('#front').waitFor();
   await frame.locator('body').evaluate(()=>new Promise((resolve,reject)=>{let tries=0;const poll=()=>{if([...document.images].every(i=>i.complete&&i.naturalWidth>0))resolve();else if(++tries>100)reject(Error('Image load failed'));else setTimeout(poll,50)};poll()}));
   await frame.getByRole('button').click();
   const text=await frame.locator('#back').innerText();
   if(!text.includes('Counterplay:')||/\b(INFERRED|UNVERIFIED|SUPPORTED|confidence|Patch)\b/i.test(text))throw Error('Learning-text separation failed');
   if(await page.locator('#answer').inputValue()!==c.working.row.answer)throw Error('Working editorial text not displayed');
   checked++;
  }
  const overview=state.cards.find(c=>c.champion==='Braum'&&c.working.row.slot==='-');
  const braumE=state.cards.find(c=>c.champion==='Braum'&&c.working.row.slot==='E');
  const approvalCard=state.cards.find(c=>c.champion==='Braum'&&c.content_review.status==='pending'&&c.media_review.status==='pending');
  const fallbackCard=state.cards.find(c=>c.champion==='Aphelios'&&c.id.includes('moonshot'));
  if(!overview||!braumE||!approvalCard)throw Error('Focused Braum overview/E or pending fixture records were not found');
  for(const card of [overview,braumE]){
   await page.selectOption('#champion',card.champion);
   await page.locator('#list button').filter({hasText:card.working.row.slot+' · '+card.working.row.ability}).first().click();
   if(await page.locator('#claims').isChecked()||await page.locator('#cores').isChecked()||await page.locator('#inference').isChecked()||await page.locator('#warnings').isChecked())throw Error('Content approval attestations must start unchecked');
   if(!(await page.locator('#detail').innerText()).includes('Content: '+card.content_review.status+' · Media: '+card.media_review.status))throw Error('Existing focused-card approval decision is not displayed');
  }
  await page.locator('#list button').filter({hasText:'- · '+overview.working.row.ability}).first().click();
  const overviewText=await page.locator('#detail').innerText();
  for(const label of ['Riot: Concussive Blows','Riot: Unbreakable','Riot: Stand Behind Me'])if(!overviewText.includes(label))throw Error('Overview source mapping missing '+label);
  await page.locator('#list button').filter({hasText:'E · '+braumE.working.row.ability}).first().click();
  const eText=await page.locator('#detail').innerText();
  for(const mechanic of ['projectiles','first eligible instance of champion damage','subsequent eligible damage'])if(!eText.toLowerCase().includes(mechanic.toLowerCase()))throw Error('Braum E required core mechanic missing '+mechanic);
  for(const label of ['Riot: Unbreakable','Wiki: Unbreakable'])if(!eText.includes(label))throw Error('Braum E source mapping missing '+label);
  if(await page.locator('details summary').filter({hasText:'Other champion conflicts'}).evaluate(el=>el.parentElement.open))throw Error('Unrelated champion conflicts should remain collapsed');
  if(offlineState){
   await page.locator('#list button').filter({hasText:approvalCard.working.row.slot+' · '+approvalCard.working.row.ability}).first().click();
   if(await page.locator('[data-source]:checked').count())throw Error('Pending-card source selections must not be prechecked');
   await page.locator('#reviewer').fill('Browser Tester');
   await page.locator('#combinedApprove').click();
   if(!(await page.locator('#message').innerText()).includes('confirm both'))throw Error('Combined approval must require explicit confirmation');
   await page.locator('#combinedConfirm').check();
   await page.locator('#combinedApprove').click();
   if(!(await page.locator('#message').innerText()).includes('select at least one'))throw Error('Combined approval must require explicit evidence selection');
   await page.locator('[data-source]').first().check();
   await page.locator('#notes').fill('Keep this note after approval refresh.');
   await page.locator('#mediaReviewDetails > summary').click();
   await page.locator('#mediaConfirm').check();
   await page.locator('#combinedApprove').click();
   if(postBodies.length!==1||postBodies[0].action!=='approve-content-and-media'||postBodies[0].id!==approvalCard.id)throw Error('Combined review did not use one combined action for the selected pending card');
   await page.waitForFunction(()=>document.querySelector('#reviewStatus')?.textContent.includes('Content: approved · Media: approved'));
   if(await page.locator('#notes').inputValue()!=='Keep this note after approval refresh.'||!await page.locator('#mediaConfirm').isChecked())throw Error('Unsubmitted form state was lost after content/media approval refresh');
   if(!(await page.locator('#reviewStatus').innerText()).includes('Content: approved · Media: approved'))throw Error('Both separate approval records were not reflected after combined approval: '+await page.locator('#reviewStatus').innerText()+'; action='+JSON.stringify(postBodies[0]));
   if(!await page.locator('#nextPending').isVisible())throw Error('Next pending card control was not offered after approval');
   if(!(await page.locator('#detail').innerText()).includes(approvalCard.id))throw Error('Card navigation advanced without an explicit click');
   await page.locator('#nextPending').click();
   if((await page.locator('#detail').innerText()).includes(approvalCard.id))throw Error('Next pending card button did not navigate');
   if(await page.locator('#combinedConfirm').isChecked()||await page.locator('[data-source]:checked').count())throw Error('Card-specific attestations or evidence carried to another card');
   await page.locator('summary').filter({hasText:'Separate approval actions'}).click();
   await page.locator('#reviewer').fill('');
   await page.locator('#contentReject').click();
   if(!(await page.locator('#message').innerText()).includes('reviewer name'))throw Error('Reviewer name must remain required for rejection');
   await page.locator('#reviewer').fill('Browser Tester');
   if(!fallbackCard||!fallbackCard.media.fallback)throw Error('Aphelios Moonshot fallback fixture is unavailable');
   await page.selectOption('#champion','Aphelios');
   await page.locator('#list button').filter({hasText:fallbackCard.working.row.slot+' · '+fallbackCard.working.row.ability}).first().click();
   if(await page.locator('#reviewer').inputValue()!=='Browser Tester')throw Error('Reviewer name did not persist across champion selection');
   await page.locator('#combinedConfirm').check();await page.locator('[data-source]').first().check();
   await page.locator('#combinedApprove').click();
   if(!(await page.locator('#message').innerText()).includes('static fallback'))throw Error('Missing static fallback reason is not shown in the UI');
  }
  if(offlineState&&postBodies.length!==1)throw Error('Expected exactly one isolated combined-approval request');
  if(!offlineState&&posts.length)throw Error('Live verification made a review mutation');
  await page.screenshot({path:path.join(root,'build/phase3_3/review-dashboard.png'),fullPage:false});
  const probe=path.join(root,'build/phase3_3/published-field-probe/overview.html');
  if(fs.existsSync(probe)){
   await page.goto(pathToFileURL(probe).href);
   if(await page.locator('.bottom').isVisible()||await page.locator('.source').isVisible())throw Error('Unknown patch/QA footer visible with frozen production templates');
   if(!(await page.locator('body').innerText()).includes('Counterplay:'))throw Error('Published-note Counterplay missing');
  }
  fs.writeFileSync(path.join(root,'build/phase3_3/browser-review-checks.json'),JSON.stringify({cards_checked:checked,focused_cards:['Braum overview','Braum E','pending Braum combined approval','Aphelios Moonshot exception validation'],mode:offlineState?'in-memory browser fixture':'live review service',post_requests:posts.length,passed:true,published_field_probe:!offlineState&&fs.existsSync(probe)},null,2)+'\n');
  process.stdout.write(`Checked ${checked} editorial previews, combined approval state, card-specific form persistence, and fallback messaging.\n`);
 }finally{await browser.close()}
})().catch(e=>{process.stderr.write(e.stack+'\n');process.exitCode=1});
