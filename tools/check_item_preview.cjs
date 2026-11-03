const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto');
const {pathToFileURL}=require('node:url');
const runtime=process.env.LEAGUE_ANKI_PLAYWRIGHT||path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {chromium}=require(runtime);
const root=path.resolve(__dirname,'..'), folder=path.join(root,'build/items-prototype');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.LEAGUE_ANKI_BROWSER||'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 try{
  const page=await browser.newPage({viewport:{width:850,height:1100}}), checks=[];
  const cards=JSON.parse(fs.readFileSync(path.join(folder,'cards.json'))).cards;
  for(const card of cards){
   const name=card.id.toLowerCase().replace(/[^a-z0-9-]+/g,'-').replace(/^-|-$/g,'')+'.html';
   await page.goto(pathToFileURL(path.join(folder,'previews',name)).href);
   await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));
   const front=await page.locator('#front').innerText();
   if(/Patch 26.21|League ability|Wiki/.test(front)||await page.locator('#front a').count())throw Error('Source/patch leaked onto front');
   let animation='not applicable';
   const gif=page.locator('#front img.ability-gif');
   if(await gif.count()){
    const hashes=new Set();
    for(let i=0;i<18;i++){
     hashes.add(crypto.createHash('sha256').update(await gif.screenshot()).digest('hex'));
     if(hashes.size>1)break;
     await page.waitForTimeout(420);
    }
    if(hashes.size<2)throw Error('GIF did not visibly animate: '+card.id);
    animation='visible frame change in browser';
   }
   await page.getByRole('button').click();
   if(!await page.locator('#back').isVisible())throw Error('Answer toggle');
   if(await page.locator('#back .bottom').count()!==1)throw Error('Back footer');
   await page.locator('#back a').evaluateAll(anchors=>anchors.forEach(a=>a.addEventListener('click',e=>{e.preventDefault();window.clickedSource=a.href;})));
   const links=[];
   for(const a of await page.locator('#back a').all()){
    const href=await a.getAttribute('href');if(!/^https:\/\//.test(href))throw Error('Invalid source URL');
    await a.click();if(await page.evaluate(()=>window.clickedSource)!==href)throw Error('Source click target mismatch');links.push(href);
   }
   const keywords=await page.locator('#back .keyword').evaluateAll(xs=>xs.map(x=>({text:x.textContent,color:getComputedStyle(x).color})));
   if(card.id==='item:3140:cleanse_limits:L2' && await page.locator('#back .learning-section').count()!==4)throw Error('QSS sections');
   for(const width of [850,360]){
    await page.setViewportSize({width,height:1100});
    if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('Horizontal overflow: '+card.id);
    if(card.id==='item:3140:cleanse_limits:L2'||card.id==='term:charm:L0'||card.id==='term:stasis:L0')await page.screenshot({path:path.join(folder,name.replace('.html','-')+width+'.png'),fullPage:true});
   }
   await page.setViewportSize({width:850,height:1100});
   checks.push({id:card.id,animation,links,keywords,desktop_and_mobile:'passed'});
  }
  fs.writeFileSync(path.join(folder,'browser-checks.json'),JSON.stringify({cards:checks.length,all_passed:true,checks,limitations:'Headless Chromium rendering and playback; no desktop Anki WebView or mobile-device playback test. Source click targets checked without network navigation.'},null,2));
  process.stdout.write('All '+checks.length+' previews passed; six GIFs visibly animated; source click targets and 360/850px layouts passed.\n');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
