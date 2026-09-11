const { chromium } = require('playwright');
(async () => {
  const exe = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
  const browser = await chromium.launch({ headless: true, executablePath: exe, args:['--no-sandbox'] });
  const page = await browser.newPage();
  page.on('request', req => {
    const u=req.url();
    if (u.includes('get') || u.includes('api') || u.includes('jobfair') || u.includes('job') || u.includes('bysjy')) {
      if (!u.endsWith('.js') && !u.endsWith('.css') && !u.endsWith('.png')) console.log('REQ', req.method(), u);
    }
  });
  page.on('response', async resp=>{
    const u=resp.url();
    if (u.includes('get') && (u.includes('jobfair')||u.includes('job')||u.includes('career'))) {
      try{
        const t=await resp.text();
        console.log('RESP', u, resp.status(), t.slice(0,5000));
      }catch(e){}
    }
  });
  console.log('goto jobfairs');
  await page.goto('https://jy.hnust.edu.cn/module/jobfairs', { waitUntil: 'networkidle', timeout:40000 });
  await page.waitForTimeout(7000);
  const links = await page.$$eval("a[href*='/detail/jobfair']", els => els.map(e=>e.getAttribute('href')).slice(0,5));
  console.log('jobfair links', links);
  const perf = await page.evaluate(()=>performance.getEntriesByType('resource').map(r=>r.name).filter(u=>u.includes('get')));
  console.log('perf get', perf.slice(0,20));
  await browser.close();
})();
