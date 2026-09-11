import json, pathlib, sys, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "backend"))
from app.database import SessionLocal, init_db
from app.models import Job

# 优先真实数据，其次样本
candidates = [
    pathlib.Path("data/real/jobs.json"),
    pathlib.Path("data/real/careers.json"),
    pathlib.Path("data/samples/hnust_sample.json"),
]
data=[]
for p in candidates:
    if p.exists():
        try:
            d=json.loads(p.read_text(encoding="utf-8"))
            # jobs.json is normalized with title/company_name, careers.json likewise
            # 若是 careers，直接也作为 job 写入以便检索
            data.extend(d)
            if len(data)>=800:
                break
        except Exception as e:
            print(f"load {p} err {e}")
# 去重按 title+company
uniq={}
for x in data:
    title=x.get("title") or x.get("job_name") or x.get("meet_name")
    comp=x.get("company_name")
    if not title or not comp:
        continue
    key=(comp, title)
    if key not in uniq:
        uniq[key]=x
data=list(uniq.values())[:1200]

init_db()
db=SessionLocal()
db.query(Job).delete()
db.commit()
for item in data:
    title=item.get("title") or item.get("job_name") or item.get("meet_name") or "未命名"
    comp=item.get("company_name") or "未知企业"
    # salary 解析
    smin=item.get("salary_min")
    smax=item.get("salary_max")
    sraw=item.get("salary") or item.get("salary_raw")
    if not smin and sraw:
        m=re.search(r"(\d+)[Kk]\s*[-~]+\s*(\d+)[Kk]", sraw)
        if m:
            smin=int(m.group(1))*1000
            smax=int(m.group(2))*1000
    # location
    city=item.get("city_name") or item.get("job_city") or item.get("location_city") or (item.get("location_normalized") or {}).get("city")
    loc_raw=item.get("location") or item.get("address") or item.get("location_raw") or city
    cat=item.get("category") or item.get("industry_category") or "其他"
    desc=item.get("description") or item.get("about_major") or item.get("professionals") or ""
    job=Job(
        title=title[:120],
        company_name=comp[:80],
        category=cat,
        description=desc[:4000],
        requirements=item.get("requirements") or item.get("professionals") or "",
        skills=item.get("skills") or [],
        salary_raw=sraw,
        salary_min=smin,
        salary_max=smax,
        location_raw=loc_raw,
        location_city=city,
        location_province=(item.get("location_normalized") or {}).get("province"),
        source=item.get("source") or "hnust",
        source_url=item.get("detail_url") or item.get("source_url") or f"https://jy.hnust.edu.cn/detail/career?id={item.get('career_talk_id') or item.get('publish_id') or ''}",
        source_type=item.get("source_type") or ("careers" if item.get("career_talk_id") else "jobs"),
        publish_date=item.get("publish_time") or item.get("meet_day") or item.get("publish_date"),
        crawl_time=item.get("crawl_time"),
    )
    db.add(job)
db.commit()
print(f"seeded {db.query(Job).count()} jobs from {len(data)} source items (deduped)")
db.close()
