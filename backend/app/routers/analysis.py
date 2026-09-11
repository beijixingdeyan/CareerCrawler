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
        # convert to dict like sample
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
    # fallback samples
    for p in [pathlib.Path("data/samples/crawl_latest.json"), pathlib.Path("data/samples/hnust_sample.json")]:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except: pass
    return []

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    jobs = _load_jobs(db)
    companies = db.query(Company).all()
    data = dashboard(jobs, companies)
    # 针对计科专业的提示
    data["cs_insight"] = {
        "message": "计科 2027 届 813 人（软件139/信安129/物联网116/大数据131/计科298）+ 硕士106 + 博士13，主战场为 开发/算法/安全/大数据",
        "focus_skills": ["Java", "Python", "Vue/React", "SpringBoot", "MySQL", "Redis", "Docker", "机器学习"],
        "hot_cities": ["长沙", "深圳", "广州", "杭州", "武汉"],
    }
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
