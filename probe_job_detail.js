const { chromium } = require('playwright');
(async()=>{
  const exe="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
  const browser=await chromium.launch({headless:true,executablePath:exe,args:['--no-sandbox']});
  const page=await browser.newPage();
  page.on('request',r=>{
    const u=r.url();
    if(u.includes('getjob')||u.includes('getcompany')||u.includes('detail')||u.includes('publish')){
      if(!u.endsWith('.js')&&!u.endsWith('.css')&&!u.includes('hm.baidu')) console.log('REQ',r.method(),u);
    }
  });
  page.on('response',async resp=>{
    const u=resp.url();
    if(u.includes('getjob')||u.includes('getcompany')||u.includes('publish')){
      try{
        const t=await resp.text();
        console.log('RESP',u,resp.status(),t.slice(0,8000));
      }catch(e){}
    }
  });
  console.log('goto job detail');
  await page.goto('https://jy.hnust.edu.cn/detail/job?id=2616482', {waitUntil:'networkidle',timeout:40000}); // management trainee from fair 64
  await page.waitForTimeout(6000);
  const body=await page.content();
  require('fs').writeFileSync('probe_job_detail.html',body,'utf-8');
  console.log('body len',body.length);
  console.log(body.slice(body.indexOf('publish')-2000, body.indexOf('publish')+5000).slice(0,4000));
  await browser.close();
})();
