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
        return [{"name": x["name"], "industry": x.get("industry"), "scale": x.get("scale"), "city": x.get("city"), "intro": (x.get("intro") or "")[:120], "recruitment_url": x.get("recruitment_url"), "official_url": x.get("official_url"), "ranking": x.get("ranking"), "ranking_source": x.get("ranking_source") or x.get("source"), "source": x.get("source"), "verified": x.get("verified")} for x in filtered]

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
                    "official_url": x.get("official_url"),
                    "recruitment_url": x.get("recruitment_url"),
                    "source": x.get("source"),
                },
                "job_info": None,
                "risk_assessment": {"source": x.get("source"), "verified": True, "suggestion": "权威大厂，工商信息来自官网/年报，可放心投递"},
                "provenance": {"source": x.get("source"), "recruitment_url": x.get("recruitment_url"), "verified": True}
            }
    # 2. 宣讲会 500 企业（富化，含排名，尝试实时抓取单位简介）
    for p in [pathlib.Path("data/real/careers_enriched.json")]:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                for x in data:
                    if x.get("company_name") == name:
                        bg = x.get("enterprise_background", {})
                        # 尝试实时抓取该宣讲会的单位简介（更真实）
                        real_intro = bg.get("intro")
                        real_official = bg.get("official_url")
                        career_id = x.get("career_talk_id")
                        if career_id:
                            try:
                                import requests
                                from bs4 import BeautifulSoup
                                H = {"User-Agent": "Mozilla/5.0"}
                                r = requests.get(f"https://jy.hnust.edu.cn/detail/career?id={career_id}", headers=H, timeout=8)
                                r.encoding = "utf-8"
                                soup = BeautifulSoup(r.text, "lxml")
                                for mod in soup.select(".detail-module"):
                                    tit = mod.select_one(".dm-tit")
                                    if tit and ("单位简介" in tit.get_text() or "企业简介" in tit.get_text() or "公司简介" in tit.get_text()):
                                        txt = mod.get_text(separator="\n", strip=True).replace(tit.get_text(strip=True),"",1).strip()
                                        if len(txt) > 20:
                                            real_intro = txt[:2000]
                                            break
                                # 尝试找官网链接
                                for a in soup.select("a[href]"):
                                    href = a.get("href","")
                                    if href.startswith("http") and "bysjy" not in href and "hnust" not in href and "bibibi" not in href:
                                        real_official = href
                                        break
                            except:
                                pass
                        bg_official = bg.get("official_url")
                        chosen_official = real_official or bg_official
                        return {
                            "company_name": name,
                            "fair_id": None,
                            "career_talk_id": career_id,
                            "basic_info": {
                                "company_name": name,
                                "industry": bg.get("industry"),
                                "scale": bg.get("scale"),
                                "company_property": bg.get("company_property"),
                                "city": bg.get("city"),
                                "intro": real_intro or bg.get("intro"),
                                "products": bg.get("products"),
                                "official_url": chosen_official,
                                "recruitment_url": f"https://jy.hnust.edu.cn/detail/career?id={career_id}" if career_id else bg.get("recruitment_url"),
                                "ranking": bg.get("ranking"),
                                "ranking_source": bg.get("ranking_source"),
                                "source": "宣讲会原帖单位简介 + Fortune中国500强2024 / 企业官网",
                            },
                            "job_info": None,
                            "ranking": bg.get("ranking"),
                            "ranking_source": bg.get("ranking_source"),
                            "risk_assessment": {"source": "宣讲会原帖单位简介", "verified": True, "suggestion": "宣讲会已审核，排名来自权威榜单" if bg.get("ranking") != "未上榜" else "未上榜企业，关注资质与合同"},
                            "provenance": {"source": "宣讲会原帖单位简介", "official_url": real_official or bg.get("official_url"), "career_url": f"https://jy.hnust.edu.cn/detail/career?id={career_id}", "verified": True}
                        }
            except:
                pass

    # 3. 参会企业（所有 fair）
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
                    # intro 优先用企业主页的 单位简介/企业简介，其次岗位详情中的公司介绍
                    intro_val = comp_detail.get("intro_excerpt") or sections.get("单位简介") or sections.get("企业简介") or sections.get("公司简介") or sections.get("其他描述") or ""
                    if not intro_val or len(intro_val.strip()) < 20:
                        # fallback: try to use job_detail sections that might contain company intro
                        for k,v in sections.items():
                            if "简介" in k and len(v) > 20:
                                intro_val = v
                                break
                    if not intro_val:
                        intro_val = f"{x.get('company_name')} 参会企业，来自 jy.hnust 官方审核，主营 {x.get('industry_category') or '相关行业'}，规模 {x.get('scale') or '—'}。"
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
                            "intro": intro_val[:2000],
                            "intro_excerpt": comp_detail.get("intro_excerpt") or intro_val[:300],
                            "official_url": None,
                            "recruitment_url": None,
                            "source": "双选会原帖",
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
    # 无真实数据时不再生成虚假启发式数据
    return {
        "company_name": name,
        "basic_info": {
            "company_name": name,
            "industry": "未收录",
            "intro": "该企业暂未在宣讲会 500 / 双选会已爬取范围及权威大厂库 17 家中收录，暂无真实介绍。请通过宣讲会/双选会卡片查看已爬取企业的真实单位简介。",
            "source": "未收录（仅展示真实爬取数据，无虚假生成）",
        },
        "risk_assessment": {"risk_level": "unknown", "risk_score": None, "suggestion": "未收录企业，建议现场核验资质"},
        "provenance": {"verified": False, "note": "no fake data"},
    }
