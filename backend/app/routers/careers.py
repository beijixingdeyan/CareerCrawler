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
    total = len(filtered)
    start = (page-1)*page_size
    items = filtered[start:start+page_size]
    return {"total": total, "page": page, "page_size": page_size, "items": items}

@router.get("/stats")
def stats():
    data = _load_careers()
    return {"total": len(data), "sample": data[:1]}
