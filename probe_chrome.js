const { chromium } = require('playwright');
(async () => {
  const exe = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
  const browser = await chromium.launch({ headless: true, executablePath: exe, args:['--no-sandbox','--disable-blink-features=AutomationControlled'] });
  const page = await browser.newPage({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36' });
  const apiRequests = [];
  page.on('request', req => {
    const u = req.url();
    if (u.includes('career') || u.includes('jobfair') || u.includes('api') || u.includes('bysjy') || u.includes('jy.hnust')) {
      // filter out static css/js
      if (!u.endsWith('.css') && !u.endsWith('.png') && !u.endsWith('.js') && !u.includes('hm.baidu')) {
        console.log('REQ', req.method(), u);
        apiRequests.push(u);
      }
    }
  });
  page.on('response', async resp => {
    const u = resp.url();
    if ((u.includes('career') || u.includes('jobfair') || u.includes('api')) && resp.request().method() !== 'GET' ) {
      // also catch GET api
    }
    if (u.includes('api') || (u.includes('career') && resp.headers()['content-type']?.includes('json'))){
      try{
        const t = await resp.text();
        console.log('RESP', u, resp.status(), t.slice(0,5000));
      }catch(e){}
    }
  });
  console.log('goto');
  await page.goto('https://jy.hnust.edu.cn/module/careers', { waitUntil: 'networkidle', timeout: 40000 });
  await page.waitForTimeout(7000);
  // dump resources
  const perf = await page.evaluate(() => performance.getEntriesByType('resource').map(r=>r.name));
  const filtered = perf.filter(u=>u.includes('career')||u.includes('api')||u.includes('jobfair')||u.includes('bysjy'));
  console.log('perf filtered', filtered);
  // also dump all XHR/fetch via window.performance but also check page's JS
  const allUrls = await page.evaluate(() => performance.getEntriesByType('resource').map(r=>({name:r.name, initiator:r.initiatorType})));
  console.log('all resources initiator', allUrls.filter(x=>x.name.includes('jy.')).slice(0,20));
  const links = await page.$$eval("a[href*='/detail/career']", els => els.map(e=>({href:e.getAttribute('href'), text:e.innerText.slice(0,80)})));
  console.log('career links', links.length, links.slice(0,5));
  const body = await page.content();
  require('fs').writeFileSync('probe_chrome_render.html', body, 'utf-8');
  console.log('body len', body.length);
  // try extract pagination
  const pagination = await page.evaluate(() => document.documentElement.outerHTML);
  const idx = pagination.indexOf('pagination');
  if(idx>-1) console.log(pagination.slice(idx-2000, idx+5000).slice(0,4000));
  else console.log('no pagination string');
  // also try to find any JSON data in page
  const jsonDump = await page.evaluate(() => {
    const html = document.documentElement.innerHTML;
    const m = html.match(/career[\s\S]{0,500}/);
    return m ? m[0].slice(0,2000) : 'no';
  });
  console.log('jsonDump', jsonDump);
  await browser.close();
})();
