const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' });
  const reqs = [];
  page.on('request', req => {
    const u = req.url();
    if (u.includes('career') || u.includes('jobfair') || u.includes('api') || u.includes('bysjy') || u.includes('hnust')) {
      console.log('REQ', req.method(), u);
      reqs.push(u);
    }
  });
  page.on('response', async resp => {
    const u = resp.url();
    if (u.includes('career') || u.includes('jobfair') || u.includes('api') || u.includes('bysjy')) {
      try {
        const status = resp.status();
        const headers = resp.headers();
        // try json
        let body = '';
        const ct = headers['content-type'] || '';
        if (ct.includes('json') || u.includes('api')) {
          body = await resp.text();
          console.log('RESP JSON', u, status, body.slice(0,3000));
        } else {
          // ignore large html
        }
      } catch(e){ console.log('resp err', e.message)}
    }
  });
  console.log('goto careers');
  await page.goto('https://jy.hnust.edu.cn/module/careers', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(6000);
  const content = await page.content();
  require('fs').writeFileSync('probe_rendered_node.html', content, 'utf-8');
  console.log('content len', content.length);
  const perf = await page.evaluate(() => performance.getEntriesByType('resource').map(r=>r.name).filter(u=>u.includes('career')||u.includes('api')||u.includes('bysjy')||u.includes('hnust')));
  console.log('perf', perf.slice(0,20));
  const links = await page.$$eval("a[href*='/detail/career']", els => els.map(e=>({href:e.getAttribute('href'), text:e.innerText.slice(0,60)})));
  console.log('career links', links.length);
  console.log(links.slice(0,5));
  const htmlSnippet = await page.evaluate(() => document.documentElement.outerHTML.slice(0,15000));
  console.log('HTML snippet', htmlSnippet.slice(htmlSnippet.indexOf('pub-list')-1000, htmlSnippet.indexOf('pub-list')+4000));
  // check pagination text
  const pagination = await page.evaluate(() => document.body.innerHTML.slice(0,20000).match(/pagination[\s\S]{0,2000}/));
  console.log('pagination match', pagination ? pagination[0].slice(0,2000) : 'none');
  // try to find XHR inside page evaluate fetch list
  const xhrDump = await page.evaluate(async () => {
    // try to find any global data
    return {
      G_MODULES: typeof G_MODULES !== 'undefined' ? G_MODULES : null,
      G_CONFIG: typeof G_CONFIG !== 'undefined' ? G_CONFIG : null,
      body: document.body.innerHTML.slice(0,5000)
    };
  });
  console.log('xhrDump', JSON.stringify(xhrDump, null, 2).slice(0,3000));
  await browser.close();
})();
