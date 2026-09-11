from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "crawler"))
from company_researcher import research_company
from ..database import get_db
from ..models import Company, Job

router = APIRouter(prefix="/api/companies", tags=["companies"])

def _load_fair64():
    for p in [pathlib.Path("data/real/fair30003_64.json"), pathlib.Path("data/samples/fair30003_64.json")]:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except:
                pass
    return []

@router.get("")
def list_companies(q: Optional[str] = None, db: Session = Depends(get_db)):
    fair = _load_fair64()
    if fair:
        # 64 条岗位 = 64 行（不按公司去重，保留 64 家参会岗位的完整列表）
        items = fair
        if q:
            ql = q.lower()
            items = [x for x in items if ql in x.get("company_name","").lower() or ql in x.get("job_name","").lower()]
        return [{"name": x["company_name"], "industry": x.get("industry_category"), "scale": x.get("scale"), "city": x.get("city_name"), "property": x.get("company_property"), "job_name": x.get("job_name"), "salary": x.get("salary"), "publish_id": x.get("publish_id"), "from": "fair30003_real"} for x in items[:64]]
    query = db.query(Company)
    if q:
        query = query.filter(Company.name.like(f"%{q}%"))
    items = query.order_by(Company.created_at.desc()).limit(50).all()
    if items:
        return [{"id": c.id, "name": c.name, "industry": c.industry, "risk_level": c.risk_level, "risk_score": c.risk_score, "staff_count_range": c.staff_count_range} for c in items]
    jobs = db.query(Job).all()
    if jobs:
        names = sorted(set(j.company_name for j in jobs))
        if q:
            names = [n for n in names if q.lower() in n.lower()]
        return [{"name": n, "industry": "信息传输、软件和信息技术服务业", "risk_level": "low" if "科技" in n else "unknown", "staff_count_range": "未知", "from": "aggregated"} for n in names[:50]]
    return []

@router.get("/{name}")
def get_company(name: str, db: Session = Depends(get_db)):
    fair = _load_fair64()
    for x in fair:
        if x.get("company_name") == name:
            jd = x.get("job_detail", {}) if isinstance(x.get("job_detail"), dict) else {}
            sections = jd.get("sections", {}) if isinstance(jd, dict) else {}
            benefits = x.get("benefits") or (jd.get("benefits_parsed") if isinstance(jd, dict) else []) or []
            comp_detail = x.get("company_detail", {}) if isinstance(x.get("company_detail"), dict) else {}
            return {
                "company_name": name,
                "fair_id": "30003",
                "fair_title": "湖南科技大学2027届计算机类毕业生专场招聘会",
                "basic_info": {
                    "company_name": name,
                    "industry": x.get("industry_category"),
                    "company_property": x.get("company_property"),
                    "scale": x.get("scale"),
                    "city": x.get("city_name"),
                    "logo": x.get("logo_url"),
                    "view_count": x.get("view_count"),
                    "intro_excerpt": comp_detail.get("intro_excerpt") or sections.get("企业简介") or sections.get("其他描述") or "",
                    "full_text_excerpt": (comp_detail.get("full_text_excerpt","") or "")[:800],
                },
                "job_info": {
                    "job_name": x.get("job_name"),
                    "publish_id": x.get("publish_id"),
                    "detail_url": jd.get("detail_url") if isinstance(jd, dict) else f"https://jy.hnust.edu.cn/detail/job?id={x.get('publish_id')}",
                    "salary": x.get("salary"),
                    "degree_require": x.get("degree_require"),
                    "job_number": x.get("job_number"),
                    "about_major": x.get("about_major"),
                    "benefits": benefits,
                    "requirements": x.get("requirements") or sections.get("岗位要求") or sections.get("职位要求") or "",
                    "description": x.get("description") or sections.get("职位描述") or "",
                    "sections": sections,
                },
                "risk_assessment": {"source": "jy.hnust 官方审核参会单位", "verified": True, "suggestion": "学校已审核营业执照，现场核验合同与社保，警惕培训费押金"},
                "provenance": {"api": "https://jy.hnust.edu.cn/module/list_jobfair_company?fair_id=30003", "job_detail_url": f"https://jy.hnust.edu.cn/detail/job?id={x.get('publish_id')}", "company_detail_url": f"https://jy.hnust.edu.cn/detail/company?id={x.get('company_id')}", "verified": True}
            }
    c = db.query(Company).filter(Company.name == name).first()
    if c:
        return {"company_name": c.name, "basic_info": c.basic_info, "risk_assessment": c.risk_assessment, "industry": c.industry, "overall_score": c.overall_score, "research_time": c.research_time}
    job = db.query(Job).filter(Job.company_name == name).first()
    ctx = job.description[:400] if job else ""
    result = research_company(name, ctx)
    try:
        new = Company(name=name, industry=result["basic_info"]["industry"], sub_industry=result["basic_info"]["sub_industry"], staff_count_range=result["basic_info"]["staff_count_range"], risk_level=result["risk_assessment"]["risk_level"], risk_score=result["risk_assessment"]["risk_score"], overall_score=str(result["overall_score"]), basic_info=result["basic_info"], risk_assessment=result["risk_assessment"], research_time=result["research_time"])
        db.add(new)
        db.commit()
    except Exception:
        db.rollback()
    return result
