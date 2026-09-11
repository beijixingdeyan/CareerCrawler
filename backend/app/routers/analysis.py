from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import json, pathlib
from ..database import get_db
from ..models import Job, Company
from ..services.analyzer import dashboard

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

def _load_jobs(db: Session):
    jobs_db = db.query(Job).all()
    if jobs_db:
        out=[]
        for j in jobs_db:
            out.append({
                "title": j.title,
                "company_name": j.company_name,
                "category": j.category,
                "skills": j.skills or [],
                "salary_min": j.salary_min,
                "salary_max": j.salary_max,
                "location_raw": j.location_raw,
                "location_city": j.location_city,
                "publish_date": j.publish_date,
                "crawl_time": j.crawl_time,
                "source_type": j.source_type,
            })
        return out
    #优先真实数据
    for p in [pathlib.Path("data/real/jobs.json"), pathlib.Path("data/real/careers.json"), pathlib.Path("data/samples/crawl_latest.json"), pathlib.Path("data/samples/hnust_sample.json")]:
        if p.exists():
            try:
                data=json.loads(p.read_text(encoding="utf-8"))
                # 若是 careers 格式，需映射 salary/location
                norm=[]
                for x in data[:2000]:
                    title=x.get("title") or x.get("job_name") or x.get("meet_name")
                    smin=x.get("salary_min")
                    smax=x.get("salary_max")
                    # 统一转换为元（处理 5 -> 5000）
                    try:
                        if smin is not None and float(smin) < 1000: smin = float(smin)*1000
                        if smax is not None and float(smax) < 1000: smax = float(smax)*1000
                        if smin is not None: smin = int(smin)
                        if smax is not None: smax = int(smax)
                    except: pass
                    if (not smin or not smax) and x.get("salary"):
                        import re
                        m=re.search(r"(\d+(?:\.\d+)?)\s*[Kk]\s*[-~至]+\s*(\d+(?:\.\d+)?)\s*[Kk]", x.get("salary"))
                        if m: smin=int(float(m.group(1))*1000); smax=int(float(m.group(2))*1000)
                    norm.append({
                        "title": title,
                        "company_name": x.get("company_name"),
                        "category": x.get("category") or x.get("industry_category") or "其他",
                        "skills": x.get("skills") or [],
                        "salary_min": smin,
                        "salary_max": smax,
                        "location_raw": x.get("location") or x.get("city_name") or x.get("job_city"),
                        "location_city": x.get("city_name") or x.get("job_city") or x.get("location_city"),
                        "publish_date": x.get("publish_time") or x.get("meet_day") or x.get("publish_date"),
                        "crawl_time": x.get("crawl_time"),
                        "source_type": x.get("source_type"),
                    })
                return norm
            except: pass
    return []

def _counts():
    # 真实总数（用于大屏 KPI）
    import json, pathlib
    counts={}
    for key, path in [("careers","data/real/careers.json"),("jobfairs","data/real/jobfairs.json"),("jobs","data/real/jobs.json")]:
        p=pathlib.Path(path)
        if p.exists():
            try: counts[key]=len(json.loads(p.read_text(encoding="utf-8")))
            except: counts[key]=0
    return counts

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    jobs = _load_jobs(db)
    companies = db.query(Company).all()
    data = dashboard(jobs, companies)
    data["cs_insight"] = {
        "message": "计科 2027 届 813 人（软件139/信安129/物联网116/大数据131/计科298）+ 硕士106 + 博士13，主战场为 开发/算法/安全/大数据",
        "focus_skills": ["Java", "Python", "Vue/React", "SpringBoot", "MySQL", "Redis", "Docker", "机器学习"],
        "hot_cities": ["长沙", "深圳", "广州", "杭州", "武汉"],
    }
    # 叠加真实总数
    counts=_counts()
    data["real_counts"] = counts
    data["total_careers"] = counts.get("careers", 0)
    data["total_jobfairs"] = counts.get("jobfairs", 0)
    data["total_jobs_real"] = counts.get("jobs", 0)
    return data

@router.get("/salary")
def salary_analysis(db: Session = Depends(get_db)):
    jobs = _load_jobs(db)
    from ..services.analyzer import salary_stats, skill_ranking
    return {"salary_stats": salary_stats(jobs), "skill_rank": skill_ranking(jobs)}

@router.get("/trend")
def trend(db: Session = Depends(get_db)):
    jobs = _load_jobs(db)
    from ..services.analyzer import trend_by_date, industry_distribution
    return {"trend": trend_by_date(jobs), "industry": industry_distribution(jobs)}
