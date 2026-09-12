from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json, pathlib
from ..database import get_db
from ..models import Job
from ..services.recommender import recommend_for_user, explain_recommendation

router = APIRouter(prefix="/api/recommend", tags=["recommend"])

class UserProfile(BaseModel):
    major: Optional[str] = "计算机科学与技术"
    degree: Optional[str] = "本科"
    skills: List[str | dict] = []
    preferred_cities: List[str] = ["长沙", "深圳"]
    preferred_categories: List[str] = ["技术开发"]
    preferred_industries: List[str] = []
    clicked_fair_ids: List[str] = []

def _load_jobs(db: Session, clicked_fair_ids: List[str] = []):
    out = []
    # 1) 真实岗位：优先读 DB，其次 data/real/jobs.json，再回落样本（均为真实爬取，无 mock）
    jobs_db = db.query(Job).all()
    if jobs_db:
        for j in jobs_db:
            out.append({
                "id": j.id,
                "title": j.title,
                "company_name": j.company_name,
                "category": j.category,
                "skills": j.skills or [],
                "salary_min": j.salary_min,
                "salary_max": j.salary_max,
                "location_city": j.location_city,
                "location_raw": j.location_raw,
                "source_url": j.source_url,
                "description": j.description,
                "industry": j.industry if hasattr(j, 'industry') else None,
            })
    else:
        # 尝试 data/real 真实文件
        for p in [pathlib.Path("data/real/jobs.json"), pathlib.Path("data/samples/crawl_latest.json"), pathlib.Path("data/samples/hnust_sample.json")]:
            if p.exists():
                try:
                    data=json.loads(p.read_text(encoding="utf-8"))
                    for x in data:
                        if isinstance(x, dict) and x.get("title"):
                            out.append({
                                "id": x.get("hash") or x.get("id") or x.get("detail_url",""),
                                "title": x.get("title"),
                                "company_name": x.get("company_name"),
                                "category": x.get("category"),
                                "skills": x.get("skills") or [],
                                "salary_min": (x.get("salary_parsed") or {}).get("min") or x.get("salary_min"),
                                "salary_max": (x.get("salary_parsed") or {}).get("max") or x.get("salary_max"),
                                "location_city": (x.get("location_normalized") or {}).get("city") or x.get("location_city") or x.get("location"),
                                "location_raw": x.get("location") or x.get("location_raw"),
                                "source_url": x.get("detail_url") or x.get("source_url"),
                                "description": x.get("description"),
                                "industry": x.get("industry") or x.get("industry_category"),
                            })
                    if out:
                        break
                except: pass
    # 2) 宣讲会 500（真实）：每场转为可推荐条目，行业来自 enterprise_background
    try:
        for p in [pathlib.Path("data/real/careers_enriched.json"), pathlib.Path("data/real/careers.json")]:
            if p.exists():
                data=json.loads(p.read_text(encoding="utf-8"))
                for x in data:
                    bg = x.get("enterprise_background") or {}
                    out.append({
                        "id": f"career-{x.get('career_talk_id')}",
                        "title": x.get("title") or x.get("company_name") or "宣讲会",
                        "company_name": x.get("company_name"),
                        "category": "宣讲会",
                        "skills": [],
                        "salary_min": None,
                        "salary_max": None,
                        "location_city": x.get("city_name") or bg.get("city"),
                        "location_raw": x.get("address") or x.get("meet_place"),
                        "source_url": f"https://jy.hnust.edu.cn/detail/career?id={x.get('career_talk_id')}",
                        "description": bg.get("intro") or x.get("description") or "",
                        "industry": bg.get("industry") or x.get("industry_category"),
                    })
                break
    except: pass
    # 3) 已点击的双选会企业（真实）：按 clicked_fair_ids 拉取对应 fair 的 companies
    if clicked_fair_ids:
        for fid in clicked_fair_ids:
            for p in [pathlib.Path(f"data/real/fair_{fid}.json"), pathlib.Path(f"data/real/fair_{fid}_raw.json"), pathlib.Path(f"data/real/fair30003_64.json") if fid=="30003" else None]:
                if p and p.exists():
                    try:
                        data=json.loads(p.read_text(encoding="utf-8"))
                        for x in data:
                            out.append({
                                "id": f"fair-{fid}-{x.get('publish_id')}",
                                "title": x.get("job_name") or x.get("title") or "双选会岗位",
                                "company_name": x.get("company_name"),
                                "category": "双选会",
                                "skills": [],
                                "salary_min": None,
                                "salary_max": None,
                                "location_city": x.get("city_name"),
                                "location_raw": x.get("city_name"),
                                "source_url": f"https://jy.hnust.edu.cn/detail/job?id={x.get('publish_id')}",
                                "description": x.get("description") or x.get("requirements") or "",
                                "industry": x.get("industry_category"),
                            })
                        break
                    except: pass
    return out

@router.post("")
def recommend(profile: UserProfile, limit: int = 12, industry: Optional[str] = None, db: Session = Depends(get_db)):
    jobs = _load_jobs(db, clicked_fair_ids=profile.clicked_fair_ids or [])
    # 行业筛选（如制造业/教育等），对推荐池先过滤
    if industry:
        jobs = [j for j in jobs if industry in (j.get("industry") or "")]
    elif profile.preferred_industries:
        # 若用户已选偏好行业，则过滤
        pref = set(profile.preferred_industries)
        jobs = [j for j in jobs if any(p in (j.get("industry") or "") for p in pref)] if pref else jobs
    user_dict = profile.model_dump()
    if user_dict["skills"] and isinstance(user_dict["skills"][0], str):
        user_dict["skills"] = [{"name": s} for s in user_dict["skills"]]
    recs = recommend_for_user(user_dict, jobs, limit=limit)
    for r in recs:
        r["reasons"] = explain_recommendation(user_dict, r)
    return {"user": user_dict, "recommendations": recs, "total_pool": len(jobs)}

@router.get("/presets")
def presets():
    return {
        "cs_undergrad": {
            "major": "计算机科学与技术",
            "degree": "本科",
            "skills": ["Java", "Python", "Vue", "SpringBoot", "MySQL", "Redis"],
            "preferred_cities": ["长沙", "深圳", "广州"],
            "preferred_categories": ["技术开发"]
        },
        "security": {
            "major": "信息安全",
            "degree": "本科",
            "skills": ["Python", "渗透测试", "Linux", "Wireshark"],
            "preferred_cities": ["长沙", "北京"],
            "preferred_categories": ["技术开发", "安全类"]
        },
        "ai_bigdata": {
            "major": "数据科学与大数据技术",
            "degree": "本科",
            "skills": ["Python", "Spark", "Hadoop", "机器学习", "PyTorch"],
            "preferred_cities": ["深圳", "杭州"],
            "preferred_categories": ["技术开发"]
        }
    }
