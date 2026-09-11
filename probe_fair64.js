const { chromium } = require('playwright');
(async()=>{
  const exe="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
  const browser=await chromium.launch({headless:true,executablePath:exe,args:['--no-sandbox']});
  const page=await browser.newPage();
  page.on('request',r=>{
    const u=r.url();
    if(u.includes('fair')||u.includes('company')||u.includes('get')||u.includes('jobfair')){
      if(!u.endsWith('.js')&&!u.endsWith('.css')&&!u.endsWith('.png')&&!u.includes('hm.baidu')) console.log('REQ',r.method(),u);
    }
  });
  page.on('response',async resp=>{
    const u=resp.url();
    if((u.includes('fair')||u.includes('company')||u.includes('get')) && !u.endsWith('.js')){
      try{
        const t=await resp.text();
        if(t.length<8000) console.log('RESP',u,resp.status(),t.slice(0,6000));
        else console.log('RESP',u,resp.status(),'len',t.length,t.slice(0,4000));
      }catch(e){}
    }
  });
  console.log('goto fair 30003');
  await page.goto('https://jy.hnust.edu.cn/detail/jobfair?id=30003', {waitUntil:'networkidle',timeout:40000});
  await page.waitForTimeout(8000);
  // try click 参会单位
  const btns=await page.$$eval("a,button", els=>els.map(e=>e.innerText.slice(0,20)).filter(t=>t.includes('参会')||t.includes('单位')));
  console.log('buttons',btns);
  // click first 参会单位
  try{
    await page.click('text=参会单位', {timeout:5000});
    await page.waitForTimeout(5000);
    console.log('clicked 参会单位');
  }catch(e){ console.log('click fail',e.message)}
  const links=await page.$$eval("a[href*='/detail/com'],a[href*='/company']", els=>els.map(e=>({href:e.getAttribute('href'),text:e.innerText.slice(0,60)})));
  console.log('company links',links.length,links.slice(0,10));
  const body=await page.content();
  require('fs').writeFileSync('probe_fair_render.html',body,'utf-8');
  console.log('body len',body.length);
  const perf=await page.evaluate(()=>performance.getEntriesByType('resource').map(r=>r.name).filter(u=>u.includes('fair')||u.includes('company')||u.includes('get')));
  console.log('perf',perf);
  await browser.close();
})();
