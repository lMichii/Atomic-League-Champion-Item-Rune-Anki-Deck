/* Optional real-browser verification of generated v4 HTML, using local bundled Playwright. */
const fs=require('node:fs');
const path=require('node:path');
const os=require('node:os');
const {pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..');
const runtime=process.env.LEAGUE_ANKI_PLAYWRIGHT || path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {chromium}=require(runtime);

(async()=>{
  const run=path.resolve(process.argv[2]);
  const cards=JSON.parse(fs.readFileSync(path.join(run,'cards.json'),'utf8')).cards;
  const report=path.join(root,'build/phase3_2',path.basename(path.dirname(run)));
  const temp=path.join(report,'browser-temp'); fs.mkdirSync(temp,{recursive:true});
  const browsers=[process.env.LEAGUE_ANKI_BROWSER,
    'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Google/Chrome/Application/chrome.exe'].filter(Boolean);
  const executablePath=browsers.find(p=>fs.existsSync(p));
  const browser=await chromium.launch({headless:true,executablePath,env:{...process.env,TEMP:temp,TMP:temp}});
  try{
    const page=await browser.newPage({viewport:{width:850,height:1100}});
    const checks=[];
    for(const card of cards){
      const name=card.learning_unit?card.id.toLowerCase().replace(/[^a-z0-9-]+/g,'-').replace(/^-|-$/g,'')+'.html':(card.row.slot==='-'?'overview':card.row.slot.toLowerCase())+'.html';
      await page.goto(pathToFileURL(path.join(run,'previews',name)).href);
      await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));
      const background=await page.locator('body').evaluate(e=>getComputedStyle(e).backgroundColor);
      if(background!=='rgb(16, 19, 23)')throw Error('v4 background mismatch');
      const fronts=[await page.locator('#front').innerText()];
      await page.getByRole('button').click();
      if(!await page.locator('#back').isVisible()||await page.locator('#front').isVisible())throw Error('Front/back toggle failed');
      const faces=[...fronts,await page.locator('#back').innerText()];
      for(const text of faces){
        if(/\b(INFERRED|SUPPORTED|UNSUPPORTED|UNVERIFIED|UNAPPROVED|VERIFIED|CONFIRMED|TENTATIVE|UNCERTAIN|CONFIDENCE|METADATA|PROVENANCE|REVIEW|PROPOSAL|DRAFT|CITATION|EVIDENCE|VERIFICATION|INFERENCE|QA|WIKI|RIOT|COMMUNITYDRAGON)\b/i.test(text))throw Error('Internal QA text on a card face');
        if(!card.versioning.verified_game_patch&&/\bPatch\b/i.test(text))throw Error('Unknown patch displayed');
      }
      if(!faces[1].includes('Counterplay:'))throw Error('Natural-language Counterplay missing');
      const images=await page.locator('img').count();
      if(!images)throw Error('No rendered real media');
      checks.push({id:card.id,rendered_images:images,background,front_back_toggle:'passed',clean_learning_text:true,unknown_patch_hidden:true});
      await page.screenshot({path:path.join(report,name.replace('.html','.png')),fullPage:true});
    }
    fs.writeFileSync(path.join(report,'browser-preview-checks.json'),JSON.stringify({cards:checks.length,all_passed:true,checks},null,2)+'\n');
    process.stdout.write(`All ${cards.length} v4 previews rendered with real media, clean card text, hidden unknown patch, and working front/back controls.\n`);
  }finally{await browser.close();}
})().catch(e=>{process.stderr.write(String(e.stack)+'\n');process.exitCode=1;});
