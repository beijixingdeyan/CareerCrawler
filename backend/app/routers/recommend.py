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
    # 智能推荐池 = 宣讲会500 + 已点击双选会企业（不含岗位广场的 695 岗位，避免失效信息污染）
    # 1) 保留岗位广场逻辑但推荐中不混入，避免失效；如需可后续按需加入已过滤的 jobs
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
def recommend(profile: UserProfile, limit: int = 1000, page: int = 1, page_size: int = 12, industry: Optional[str] = None, db: Session = Depends(get_db)):
    jobs = _load_jobs(db, clicked_fair_ids=profile.clicked_fair_ids or [])
    KNOWN = {"制造业","教育","信息传输、软件和信息技术服务业","建筑业","批发和零售业","电力、热力、燃气及水生产和供应业","采矿业","科学研究和技术服务业","交通运输、仓储和邮政业","农、林、牧、渔业","住宿和餐饮业","文化、体育和娱乐业","金融业","水利、环境和公共设施管理业","公共管理、社会保障和社会组织","租赁和商务服务业"}
    if industry:
        if industry in ("其它","其他"):
            jobs = [j for j in jobs if (j.get("industry") or "") not in KNOWN]
        else:
            jobs = [j for j in jobs if industry in (j.get("industry") or "")]
    elif profile.preferred_industries:
        pref = set(profile.preferred_industries)
        has_other = any(p in ("其它","其他") for p in pref)
        if has_other:
            # 其它表示未归类
            jobs = [j for j in jobs if any(p in (j.get("industry") or "") for p in pref if p not in ("其它","其他")) or (j.get("industry") or "") not in KNOWN]
        else:
            jobs = [j for j in jobs if any(p in (j.get("industry") or "") for p in pref)] if pref else jobs
    user_dict = profile.model_dump()
    if user_dict["skills"] and isinstance(user_dict["skills"][0], str):
        user_dict["skills"] = [{"name": s} for s in user_dict["skills"]]
    # 先对全量池做推荐排序（取 limit=全量，再分页）
    recs_all = recommend_for_user(user_dict, jobs, limit=limit)
    for r in recs_all:
        r["reasons"] = explain_recommendation(user_dict, r)
    total = len(recs_all)
    start = (page-1)*page_size
    recs = recs_all[start:start+page_size]
    return {"user": user_dict, "recommendations": recs, "total": total, "total_pool": len(jobs), "page": page, "page_size": page_size}

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
