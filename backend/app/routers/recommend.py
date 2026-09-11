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

def _load_jobs(db: Session):
    jobs_db = db.query(Job).all()
    if jobs_db:
        return [{
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
        } for j in jobs_db]
    for p in [pathlib.Path("data/samples/crawl_latest.json"), pathlib.Path("data/samples/hnust_sample.json")]:
        if p.exists():
            try:
                data=json.loads(p.read_text(encoding="utf-8"))
                # normalize
                out=[]
                for x in data:
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
                    })
                return out
            except: pass
    return []

@router.post("")
def recommend(profile: UserProfile, limit: int = 12, db: Session = Depends(get_db)):
    jobs = _load_jobs(db)
    user_dict = profile.model_dump()
    # normalize skills to dict list if strings
    if user_dict["skills"] and isinstance(user_dict["skills"][0], str):
        user_dict["skills"] = [{"name": s} for s in user_dict["skills"]]
    recs = recommend_for_user(user_dict, jobs, limit=limit)
    # attach explanation
    for r in recs:
        r["reasons"] = explain_recommendation(user_dict, r)
    return {"user": user_dict, "recommendations": recs}

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
