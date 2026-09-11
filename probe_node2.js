const { chromium } = require('playwright');
(async () => {
  const exe = "C:\\Users\\HP\\AppData\\Local\\ms-playwright\\chromium-1243\\chrome-win64\\chrome.exe";
  const browser = await chromium.launch({ headless: true, executablePath: exe, args:['--no-sandbox'] });
  const page = await browser.newPage({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' });
  page.on('request', req => {
    const u = req.url();
    if (u.includes('career') || u.includes('jobfair') || u.includes('api') || u.includes('bysjy')) {
      console.log('REQ', req.method(), u);
    }
  });
  page.on('response', async resp => {
    const u = resp.url();
    if (u.includes('career') || u.includes('jobfair') || u.includes('api') || u.includes('bysjy')) {
      try {
        const status = resp.status();
        const ct = resp.headers()['content-type'] || '';
        if (ct.includes('json') || u.includes('api')) {
          const body = await resp.text();
          console.log('RESP', u, status, body.slice(0,4000));
        }
      } catch(e){}
    }
  });
  console.log('goto');
  await page.goto('https://jy.hnust.edu.cn/module/careers', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(6000);
  const links = await page.$$eval("a[href*='/detail/career']", els => els.map(e=>({href:e.getAttribute('href'), text:e.innerText.slice(0,80)})));
  console.log('career links', links.length);
  console.log(links.slice(0,5));
  const content = await page.content();
  require('fs').writeFileSync('probe_rendered2.html', content, 'utf-8');
  console.log('content len', content.length);
  const perf = await page.evaluate(() => performance.getEntriesByType('resource').map(r=>r.name).filter(u=>u.includes('career')||u.includes('api')||u.includes('bysjy')));
  console.log('perf', perf.slice(0,20));
  const htmlSnippet = await page.evaluate(() => document.documentElement.outerHTML.slice(document.documentElement.outerHTML.indexOf('pub-list')-2000, document.documentElement.outerHTML.indexOf('pub-list')+8000));
  console.log('snippet', htmlSnippet.slice(0,5000));
  await browser.close();
})();
