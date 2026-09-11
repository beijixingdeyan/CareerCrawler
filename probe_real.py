from playwright.sync_api import sync_playwright
import time, re, json, pathlib
url = "https://jy.hnust.edu.cn/module/careers"
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    # capture network
    reqs=[]
    def handle_req(req):
        u=req.url
        if "career" in u or "jobfair" in u or "api" in u or "bysjy" in u:
            print("REQ", req.method, u)
            reqs.append(u)
    page.on("request", handle_req)
    page.on("response", lambda resp: print("RESP", resp.url, resp.status) if ("career" in resp.url or "api" in resp.url) else None)
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(5000)
    content = page.content()
    pathlib.Path("probe_rendered.html").write_text(content, encoding="utf-8")
    print("content len", len(content))
    # dump perf
    perf = page.evaluate("() => performance.getEntriesByType('resource').map(r=>r.name).filter(u=>u.includes('career')||u.includes('api')||u.includes('bysjy'))")
    print("perf", perf[:20])
    # try find list items
    items = page.query_selector_all("a[href*='/detail/career']")
    print("detail/career links", len(items))
    for a in items[:5]:
        print(a.get_attribute("href"), a.inner_text()[:50])
    # pagination
    html = content
    print(html[html.find("pagination")-500: html.find("pagination")+2000] if "pagination" in html else "no pagination string")
    # try evaluate inner HTML of pub-list
    lst = page.evaluate("() => document.documentElement.outerHTML.slice(0,12000)")
    print(lst[(lst.find("pub-list")-1000): lst.find("pub-list")+3000] if "pub-list" in lst else lst[:4000])
    browser.close()
