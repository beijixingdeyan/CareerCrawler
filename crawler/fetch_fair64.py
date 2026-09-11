import requests, json, time, re, pathlib
from bs4 import BeautifulSoup

BASE="https://jy.hnust.edu.cn"
H={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}

def fetch_fair_companies(fair_id="30003"):
    total_r=requests.get(f"{BASE}/module/list_jobfair_company?is_total=1&type=0&fair_id={fair_id}", headers=H, timeout=15)
    total=int(total_r.text.strip())
    print(f"fair {fair_id} total companies/jobs: {total}")
    all_items=[]
    count=15
    pages=(total+count-1)//count
    for page in range(1, pages+1):
        start=(page-1)*count+1
        url=f"{BASE}/module/list_jobfair_company?is_total=0&start_page={page}&type=0&fair_id={fair_id}&count={count}&start={start}&_={int(time.time()*1000)}"
        r=requests.get(url, headers=H, timeout=15)
        r.encoding="utf-8"
        j=r.json()
        data=j.get("data",[])
        print(f" page {page}/{pages} -> {len(data)}")
        all_items.extend(data)
        time.sleep(0.4)
    return all_items

def parse_job_detail(publish_id):
    url=f"{BASE}/detail/job?id={publish_id}"
    try:
        r=requests.get(url, headers=H, timeout=15)
        r.encoding="utf-8"
        soup=BeautifulSoup(r.text, "lxml")
        # extract fields
        company = soup.select_one(".company-name")
        job = soup.select_one(".job-name")
        tags = [t.get_text(strip=True) for t in soup.select(".tag-item")]
        welfare = [w.get_text(strip=True) for w in soup.select(".job-welfare")]
        # 福利是 "职位诱惑：xxx" 和 "薪酬福利：xxx"
        benefits=[]
        for w in welfare:
            # w like "职位诱惑：年底双薪 绩效奖金 年度旅游"
            if "：" in w:
                benefits.append(w)
            else:
                benefits.append(w)
        # description sections
        desc={}
        for mod in soup.select(".detail-module"):
            tit=mod.select_one(".dm-tit")
            if not tit:
                continue
            title=tit.get_text(strip=True)
            # content is all .dm-text and following p
            cont=mod.get_text(separator="\n", strip=True)
            # remove title
            cont=cont.replace(title,"",1).strip()
            desc[title]=cont[:3000]
        # also try to get publish time
        pub_time=""
        for p in soup.select(".publish-time"):
            if "发布时间" in p.get_text():
                pub_time=p.get_text(strip=True)
        return {
            "publish_id": publish_id,
            "detail_url": url,
            "company_name": company.get_text(strip=True) if company else "",
            "job_name": job.get_text(strip=True) if job else "",
            "tags": tags,
            "benefits_raw": benefits,
            "benefits_parsed": [b.split("：",1)[1] if "：" in b else b for b in benefits],
            "sections": desc,
            "publish_time_raw": pub_time,
            "html_excerpt": soup.get_text(separator="\n")[:2000],
        }
    except Exception as e:
        print(f" parse job {publish_id} err {e}")
        return {"publish_id": publish_id, "error": str(e), "detail_url": url}

def parse_company_detail(company_id):
    url=f"{BASE}/detail/company?id={company_id}"
    try:
        r=requests.get(url, headers=H, timeout=15)
        r.encoding="utf-8"
        soup=BeautifulSoup(r.text, "lxml")
        # company detail page may contain intro
        # try to extract all text
        text=soup.get_text(separator="\n", strip=True)
        # find company intro section
        # look for 企业简介
        intro=""
        if "企业简介" in text:
            idx=text.index("企业简介")
            intro=text[idx: idx+2000]
        return {
            "company_id": company_id,
            "detail_url": url,
            "intro_excerpt": intro[:2000],
            "full_text_excerpt": text[:4000],
        }
    except Exception as e:
        return {"company_id": company_id, "error": str(e)}

if __name__=="__main__":
    companies=fetch_fair_companies("30003")
    print(f"fetched {len(companies)}")
    # deduplicate by company_id+publish_id
    uniq={}
    for c in companies:
        key=(c.get("company_id"), c.get("publish_id"))
        uniq[key]=c
    companies=list(uniq.values())
    print(f"after dedup {len(companies)}")
    # enrich each with job detail and company detail (limit to 64, fetch sequentially)
    enriched=[]
    for idx, c in enumerate(companies):
        pid=c.get("publish_id")
        cid=c.get("company_id")
        print(f"[{idx+1}/{len(companies)}] {c.get('company_name')} pid {pid} cid {cid}")
        job_detail=parse_job_detail(pid) if pid else {}
        # company detail only for first 10 to avoid too many requests? But user wants all 64 real, so do all
        comp_detail=parse_company_detail(cid) if cid else {}
        # merge
        merged={
            "fair_id": "30003",
            "fair_title": "湖南科技大学2027届计算机类毕业生专场招聘会",
            "company_name": c.get("company_name"),
            "company_id": cid,
            "company_property": c.get("company_property"),
            "industry_category": c.get("industry_category"),
            "scale": c.get("scale"),
            "city_name": c.get("city_name"),
            "logo_url": c.get("logo_url"),
            "publish_id": pid,
            "job_name": c.get("job_name"),
            "salary": c.get("salary"),
            "degree_require": c.get("degree_require"),
            "job_number": c.get("job_number"),
            "about_major": c.get("about_major"),
            "view_count": c.get("view_count"),
            # parsed details
            "job_detail": job_detail,
            "company_detail": comp_detail,
            # benefits and requirements from job_detail
            "benefits": job_detail.get("benefits_parsed", []),
            "requirements": job_detail.get("sections", {}).get("岗位要求") or job_detail.get("sections", {}).get("职位要求") or "",
            "description": job_detail.get("sections", {}).get("职位描述") or "",
            "raw": c,
        }
        enriched.append(merged)
        time.sleep(0.6)
        # checkpoint every 10
        if (idx+1)%10==0:
            pathlib.Path("data/real/fair30003_enriched_checkpoint.json").write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")

    out=pathlib.Path("data/real/fair30003_64.json")
    out.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved {len(enriched)} to {out}")
    # also summary
    summary={
        "fair_id":"30003",
        "title":"湖南科技大学2027届计算机类毕业生专场招聘会",
        "total": len(enriched),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source_api": f"{BASE}/module/list_jobfair_company?fair_id=30003",
        "note": "64 companies from fair API, each enriched with job detail parsing (salary/requirements/benefits) and company detail page for real background. All data from jy.hnust.edu.cn, no mock."
    }
    pathlib.Path("data/real/fair30003_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
