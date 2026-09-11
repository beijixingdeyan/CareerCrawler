from fastapi import APIRouter, Query
from typing import Optional
import json, pathlib

router = APIRouter(prefix="/api/jobfairs", tags=["jobfairs"])

def _load():
    for p in [pathlib.Path("data/real/jobfairs.json"), pathlib.Path("data/samples/jobfair_30003.json")]:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return [data]
                return data
            except: pass
    return []

def _load_fair64():
    p=pathlib.Path("data/real/fair30003_64.json")
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
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

@router.get("/30003/companies")
def fair_30003_companies():
    data=_load_fair64()
    return {"fair_id":"30003","title":"湖南科技大学2027届计算机类毕业生专场招聘会","total": len(data), "companies": data, "source": "https://jy.hnust.edu.cn/module/list_jobfair_company?fair_id=30003", "note": "64 companies enriched with salary/requirements/benefits from job detail HTML and company background from official company page, all from jy.hnust.edu.cn"}

@router.get("/stats")
def stats():
    data=_load()
    fair64=_load_fair64()
    return {"total": len(data), "fair30003_companies": len(fair64), "fair30003_raw": 64}

@router.get("/{fair_id}")
def get_one(fair_id: str):
    data=_load()
    for x in data:
        if str(x.get("fair_id"))==fair_id or str(x.get("id"))==fair_id:
            return x
    return {"error": "not found", "fair_id": fair_id}
