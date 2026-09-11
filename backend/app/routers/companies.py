from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import sys, pathlib
# allow crawler import
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "crawler"))
from company_researcher import research_company
from ..database import get_db
from ..models import Company, Job

router = APIRouter(prefix="/api/companies", tags=["companies"])

@router.get("")
def list_companies(q: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Company)
    if q:
        query = query.filter(Company.name.like(f"%{q}%"))
    items = query.order_by(Company.created_at.desc()).limit(50).all()
    if items:
        return [{"id": c.id, "name": c.name, "industry": c.industry, "risk_level": c.risk_level, "risk_score": c.risk_score, "staff_count_range": c.staff_count_range} for c in items]
    # fallback:从 jobs 聚合
    jobs = db.query(Job).all()
    if jobs:
        names = sorted(set(j.company_name for j in jobs))
        # 过滤 q
        if q:
            names = [n for n in names if q.lower() in n.lower()]
        return [{"name": n, "industry": "信息传输、软件和信息技术服务业", "risk_level": "low" if "科技" in n else "unknown", "staff_count_range": "未知", "from": "aggregated"} for n in names[:50]]
    return []

@router.get("/{name}")
def get_company(name: str, db: Session = Depends(get_db)):
    c = db.query(Company).filter(Company.name == name).first()
    if c:
        return {
            "company_name": c.name,
            "basic_info": c.basic_info,
            "risk_assessment": c.risk_assessment,
            "industry": c.industry,
            "overall_score": c.overall_score,
            "research_time": c.research_time,
        }
    # 实时调研（离线启发式）
    # 尝试找一个关联岗位以提供上下文
    job = db.query(Job).filter(Job.company_name == name).first()
    ctx = job.description[:400] if job else ""
    result = research_company(name, ctx)
    # 缓存到 DB
    try:
        new = Company(
            name=name,
            industry=result["basic_info"]["industry"],
            sub_industry=result["basic_info"]["sub_industry"],
            staff_count_range=result["basic_info"]["staff_count_range"],
            risk_level=result["risk_assessment"]["risk_level"],
            risk_score=result["risk_assessment"]["risk_score"],
            overall_score=str(result["overall_score"]),
            basic_info=result["basic_info"],
            risk_assessment=result["risk_assessment"],
            research_time=result["research_time"],
        )
        db.add(new)
        db.commit()
    except Exception:
        db.rollback()
    return result
