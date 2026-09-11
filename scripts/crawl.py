"""一键爬取脚本：可直接 python scripts/crawl.py 运行"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "crawler"))
from engine import HnustCrawler
import json, argparse

def seed_db(json_path: pathlib.Path):
    # 将爬取结果写入 SQLite
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "backend"))
    from app.database import SessionLocal, init_db
    from app.models import Job
    init_db()
    db = SessionLocal()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    # 清理旧数据（保留去重）
    added = 0
    for item in data:
        # 尝试按 source_url 去重
        url = item.get("detail_url") or item.get("source_url") or ""
        exists = db.query(Job).filter(Job.source_url == url).first()
        if exists:
            continue
        # 映射字段
        sp = item.get("salary_parsed") or {}
        ln = item.get("location_normalized") or {}
        job = Job(
            title=item.get("title") or "未命名岗位",
            company_name=item.get("company_name") or "未知企业",
            category=item.get("category") or "其他",
            description=item.get("description") or "",
            requirements=item.get("requirements") or "",
            skills=item.get("skills") or [],
            salary_raw=item.get("salary_raw") or sp.get("raw"),
            salary_min=sp.get("min") or item.get("salary_min"),
            salary_max=sp.get("max") or item.get("salary_max"),
            location_raw=item.get("location") or item.get("location_raw") or item.get("location_city"),
            location_city=ln.get("city") or item.get("location_city"),
            location_province=ln.get("province"),
            source=item.get("source") or "hnust",
            source_url=url,
            source_type=item.get("source_type") or "careers",
            publish_date=item.get("publish_date"),
            crawl_time=item.get("crawl_time"),
        )
        db.add(job)
        added += 1
    db.commit()
    db.close()
    print(f"[DB] seeded {added} new jobs")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=2)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--playwright", action="store_true")
    parser.add_argument("--seed", action="store_true", help="写入 DB")
    args = parser.parse_args()

    crawler = HnustCrawler(use_playwright=args.playwright)
    result = crawler.crawl_all(max_pages=args.pages, per_target_limit=args.limit)
    out = pathlib.Path("data/samples/crawl_latest.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] crawl {len(result)} items -> {out}")

    # 单独抓双选会详情
    jf = crawler.crawl_jobfair_detail("30003")
    (out.parent / "jobfair_30003.json").write_text(json.dumps(jf, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] jobfair 30003 -> data/samples/jobfair_30003.json")

    if args.seed:
        seed_db(out)
