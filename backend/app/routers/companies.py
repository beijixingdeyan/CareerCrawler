from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / "crawler"))
from company_researcher import research_company
from ..database import get_db
from ..models import Company, Job

router = APIRouter(prefix="/api/companies", tags=["companies"])

def _load_enterprise():
    # 权威大厂库（真实介绍 + 招聘链接）
    for p in [pathlib.Path("data/real/enterprise_library.json"), pathlib.Path("data/samples/enterprise_library.json")]:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except:
                pass
    return []

def _load_fair(fair_id: str):
    for p in [pathlib.Path(f"data/real/fair_{fair_id}.json"), pathlib.Path(f"data/real/fair30003_64.json") if fair_id=="30003" else None]:
        if p and p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except:
                pass
    return None

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
    # 优先返回权威企业库（大厂）
    ent = _load_enterprise()
    if ent:
        filtered = ent
        if q:
            ql = q.lower()
            filtered = [x for x in filtered if ql in x.get("name","").lower() or ql in x.get("industry","").lower()]
        # 同时补充参会企业（用于搜索时能搜到）
        if q:
            fair = _load_fair64()
            fair_matched = [x for x in fair if ql in x.get("company_name","").lower()]
            # 合并去重
            names = set(x["name"] for x in filtered)
            for x in fair_matched:
                if x["company_name"] not in names:
                    filtered.append({"name": x["company_name"], "industry": x.get("industry_category"), "scale": x.get("scale"), "city": x.get("city_name"), "intro": f"参会企业 · {x.get('job_name')} {x.get('salary')}", "recruitment_url": f"https://jy.hnust.edu.cn/detail/job?id={x.get('publish_id')}", "source": "jy.hnust 30003", "verified": True})
        return [{"name": x["name"], "industry": x.get("industry"), "scale": x.get("scale"), "city": x.get("city"), "intro": (x.get("intro") or "")[:120], "recruitment_url": x.get("recruitment_url"), "source": x.get("source"), "verified": x.get("verified")} for x in filtered]

    fair = _load_fair64()
    if fair:
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
    # 1. 权威库
    ent = _load_enterprise()
    for x in ent:
        if x.get("name") == name:
            return {
                "company_name": name,
                "fair_id": None,
                "basic_info": {
                    "company_name": name,
                    "industry": x.get("industry"),
                    "scale": x.get("scale"),
                    "company_property": x.get("property"),
                    "city": x.get("city"),
                    "intro": x.get("intro"),
                    "products": x.get("products"),
                    "recruitment_url": x.get("recruitment_url"),
                    "source": x.get("source"),
                },
                "job_info": None,
                "risk_assessment": {"source": x.get("source"), "verified": True, "suggestion": "权威大厂，工商信息来自官网/年报，可放心投递"},
                "provenance": {"source": x.get("source"), "recruitment_url": x.get("recruitment_url"), "verified": True}
            }
    # 2. 参会企业（所有 fair）
    # 尝试所有 fair 文件
    fair_files = list(pathlib.Path("data/real").glob("fair_*.json")) + [pathlib.Path("data/real/fair30003_64.json")]
    for pf in fair_files:
        if not pf.exists():
            continue
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
            for x in data:
                if x.get("company_name") == name:
                    jd = x.get("job_detail", {}) if isinstance(x.get("job_detail"), dict) else {}
                    sections = jd.get("sections", {}) if isinstance(jd, dict) else {}
                    benefits = x.get("benefits") or (jd.get("benefits_parsed") if isinstance(jd, dict) else []) or []
                    comp_detail = x.get("company_detail", {}) if isinstance(x.get("company_detail"), dict) else {}
                    return {
                        "company_name": name,
                        "fair_id": x.get("fair_id") or pf.stem.replace("fair_",""),
                        "basic_info": {
                            "company_name": name,
                            "industry": x.get("industry_category"),
                            "company_property": x.get("company_property"),
                            "scale": x.get("scale"),
                            "city": x.get("city_name"),
                            "logo": x.get("logo_url"),
                            "view_count": x.get("view_count"),
                            "intro": comp_detail.get("intro_excerpt") or sections.get("企业简介") or sections.get("其他描述") or x.get("company_name")+" 参会企业，来自 jy.hnust 官方审核",
                            "intro_excerpt": comp_detail.get("intro_excerpt") or "",
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
                            "requirements": x.get("requirements") or sections.get("岗位要求") or sections.get("职位要求") or sections.get("任职要求") or "详见详情",
                            "description": x.get("description") or sections.get("职位描述") or sections.get("岗位职责") or "",
                            "sections": sections,
                        },
                        "risk_assessment": {"source": "jy.hnust 官方审核参会单位", "verified": True, "suggestion": "学校已审核营业执照，现场核验合同与社保，警惕培训费押金"},
                        "provenance": {"api": f"https://jy.hnust.edu.cn/module/list_jobfair_company?fair_id={x.get('fair_id')}", "job_detail_url": f"https://jy.hnust.edu.cn/detail/job?id={x.get('publish_id')}", "company_detail_url": f"https://jy.hnust.edu.cn/detail/company?id={x.get('company_id')}", "verified": True}
                    }
        except:
            continue
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
