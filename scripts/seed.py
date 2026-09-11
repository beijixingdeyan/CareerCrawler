import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "backend"))
from app.database import SessionLocal, init_db
from app.models import Job, Company

samples = pathlib.Path("data/samples/hnust_sample.json")
data = json.loads(samples.read_text(encoding="utf-8"))
init_db()
db = SessionLocal()
# 清空旧
db.query(Job).delete()
db.commit()
for item in data:
    sp = item.get("salary_parsed") or {}
    ln = item.get("location_normalized") or {}
    job = Job(
        title=item.get("title"),
        company_name=item.get("company_name"),
        category=item.get("category") or "其他",
        description=item.get("description") or "",
        requirements=item.get("requirements") or "",
        skills=item.get("skills") or [],
        salary_raw=item.get("salary_raw") or sp.get("raw"),
        salary_min=sp.get("min"),
        salary_max=sp.get("max"),
        location_raw=item.get("location") or item.get("location_raw"),
        location_city=ln.get("city"),
        location_province=ln.get("province"),
        source=item.get("source") or "hnust",
        source_url=item.get("detail_url") or item.get("source_url"),
        source_type=item.get("source_type") or "careers",
        publish_date=item.get("publish_date"),
        crawl_time=item.get("crawl_time"),
    )
    db.add(job)
db.commit()
print(f"seeded {db.query(Job).count()} jobs")
db.close()
