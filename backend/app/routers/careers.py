from fastapi import APIRouter, Query
from typing import Optional
import json, pathlib

router = APIRouter(prefix="/api/careers", tags=["careers"])

def _load_careers():
    for p in [pathlib.Path("data/real/careers_enriched.json"), pathlib.Path("data/real/careers.json"), pathlib.Path("data/real/careers_raw.json"), pathlib.Path("data/samples/crawl_latest.json")]:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                return data
            except: pass
    return []

@router.get("")
def list_careers(
    q: Optional[str] = None,
    city: Optional[str] = None,
    industry: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=50),
):
    data = _load_careers()
    filtered = data
    if q:
        ql = q.lower()
        filtered = [x for x in filtered if ql in (x.get("title","")+x.get("company_name","")+x.get("description","")).lower()]
    if city:
        filtered = [x for x in filtered if city in (x.get("job_city") or x.get("location") or "")]
    if industry:
        KNOWN = {"制造业","教育","信息传输、软件和信息技术服务业","建筑业","批发和零售业","电力、热力、燃气及水生产和供应业","采矿业","科学研究和技术服务业","交通运输、仓储和邮政业","农、林、牧、渔业","住宿和餐饮业","文化、体育和娱乐业","金融业","水利、环境和公共设施管理业","公共管理、社会保障和社会组织","租赁和商务服务业"}
        if industry in ("其它","其他"):
            filtered = [x for x in filtered if (x.get("enterprise_background",{}).get("industry","") or x.get("industry") or x.get("industry_category") or "") not in KNOWN]
        else:
            filtered = [x for x in filtered if industry in (x.get("enterprise_background",{}).get("industry","") or x.get("industry") or x.get("industry_category") or "")]
    total = len(filtered)
    start = (page-1)*page_size
    items = filtered[start:start+page_size]
    return {"total": total, "page": page, "page_size": page_size, "items": items}

@router.get("/stats")
def stats():
    data = _load_careers()
    return {"total": len(data), "sample": data[:1]}
