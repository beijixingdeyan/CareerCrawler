const { chromium } = require('playwright');
(async () => {
  const exe = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
  const browser = await chromium.launch({ headless: true, executablePath: exe, args:['--no-sandbox'] });
  const page = await browser.newPage();
  page.on('request', req => {
    const u=req.url();
    if (u.includes('get') || u.includes('api') || u.includes('job') || u.includes('bysjy')) {
      if (!u.endsWith('.js') && !u.endsWith('.css')) console.log('REQ', req.method(), u);
    }
  });
  page.on('response', async resp=>{
    const u=resp.url();
    if (u.includes('get') && (u.includes('job')||u.includes('career'))) {
      try{
        const t=await resp.text();
        console.log('RESP', u, resp.status(), t.slice(0,4000));
      }catch(e){}
    }
  });
  console.log('goto jobs');
  await page.goto('https://jy.hnust.edu.cn/module/jobs?is_practice=0', { waitUntil: 'networkidle', timeout:40000 });
  await page.waitForTimeout(7000);
  const perf = await page.evaluate(()=>performance.getEntriesByType('resource').map(r=>r.name).filter(u=>u.includes('get')));
  console.log('perf', perf);
  await browser.close();
})();
