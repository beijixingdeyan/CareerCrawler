from fastapi import APIRouter, Query
from typing import Optional
import json, pathlib

router = APIRouter(prefix="/api/jobfairs", tags=["jobfairs"])

def _load():
    for p in [pathlib.Path("data/real/jobfairs.json"), pathlib.Path("data/samples/jobfair_30003.json")]:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                # if single object (jobfair_30003), wrap
                if isinstance(data, dict):
                    return [data]
                return data
            except: pass
    return []

@router.get("")
def list_jobfairs(q: Optional[str]=None, page: int=Query(1, ge=1), page_size: int=Query(15, ge=1, le=50)):
    data=_load()
    filtered=data
    if q:
        ql=q.lower()
        filtered=[x for x in filtered if ql in (x.get("title","")+x.get("address","")).lower()]
    total=len(filtered)
    start=(page-1)*page_size
    return {"total": total, "page": page, "page_size": page_size, "items": filtered[start:start+page_size]}

@router.get("/stats")
def stats():
    data=_load()
    return {"total": len(data)}

@router.get("/{fair_id}")
def get_one(fair_id: str):
    data=_load()
    for x in data:
        if str(x.get("fair_id"))==fair_id or str(x.get("id"))==fair_id:
            return x
    # fallback to real file with detail
    return {"error": "not found", "fair_id": fair_id}
