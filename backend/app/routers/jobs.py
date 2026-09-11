from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
import json, pathlib
from ..database import get_db
from ..models import Job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# 辅助：若 DB 为空，尝试从 data/samples 加载
SAMPLE_PATHS = [
    pathlib.Path("data/samples/crawl_latest.json"),
    pathlib.Path("../data/samples/crawl_latest.json"),
    pathlib.Path("data/samples/hnust_sample.json"),
]

def _load_samples():
    for p in SAMPLE_PATHS:
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except:
                continue
    return []

def _job_to_dict(j: Job) -> dict:
    return {
        "id": j.id,
        "title": j.title,
        "company_name": j.company_name,
        "category": j.category,
        "job_type": j.job_type,
        "description": j.description,
        "requirements": j.requirements,
        "education_req": j.education_req,
        "major_req": j.major_req,
        "skills": j.skills or [],
        "salary_raw": j.salary_raw,
        "salary_min": j.salary_min,
        "salary_max": j.salary_max,
        "salary_unit": j.salary_unit,
        "salary_currency": j.salary_currency,
        "location_raw": j.location_raw,
        "location_city": j.location_city,
        "location_province": j.location_province,
        "source": j.source,
        "source_url": j.source_url,
        "source_type": j.source_type,
        "publish_date": j.publish_date,
        "crawl_time": j.crawl_time,
        "status": j.status,
    }

@router.get("")
def list_jobs(
    q: Optional[str] = Query(None, description="关键词搜索"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    skill: Optional[str] = None,
    source_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(Job)
    if q:
        like = f"%{q}%"
        query = query.filter((Job.title.like(like)) | (Job.company_name.like(like)) | (Job.description.like(like)))
    if category:
        query = query.filter(Job.category == category)
    if city:
        query = query.filter((Job.location_city == city) | (Job.location_raw.like(f"%{city}%")))
    if source_type:
        query = query.filter(Job.source_type == source_type)
    # skill 过滤需内存（JSON）
    all_jobs = query.order_by(Job.crawl_time.desc()).all()
    if skill:
        all_jobs = [j for j in all_jobs if any(s.get("name") == skill for s in (j.skills or []))]

    # 若 DB 为空，返回样本
    if not all_jobs:
        samples = _load_samples()
        # 对样本做同等过滤
        filtered = samples
        if q:
            ql = q.lower()
            filtered = [x for x in filtered if ql in (x.get("title","")+x.get("company_name","")+x.get("description","")).lower()]
        if category:
            filtered = [x for x in filtered if x.get("category")==category]
        if city:
            filtered = [x for x in filtered if city in (x.get("location") or x.get("location_raw") or x.get("location_city") or "")]
        if skill:
            filtered = [x for x in filtered if any(s.get("name")==skill for s in (x.get("skills") or []))]
        if source_type:
            filtered = [x for x in filtered if x.get("source_type")==source_type]
        # 分页
        total = len(filtered)
        start = (page-1)*page_size
        items = filtered[start:start+page_size]
        # 适配字段
        norm = []
        for x in items:
            norm.append({
                "id": x.get("hash") or x.get("id") or x.get("detail_url","")[-12:],
                "title": x.get("title"),
                "company_name": x.get("company_name"),
                "category": x.get("category"),
                "job_type": x.get("source_type"),
                "description": x.get("description"),
                "skills": x.get("skills") or [],
                "salary_raw": x.get("salary_raw") or (x.get("salary_parsed") or {}).get("raw"),
                "salary_min": (x.get("salary_parsed") or {}).get("min") or x.get("salary_min"),
                "salary_max": (x.get("salary_parsed") or {}).get("max") or x.get("salary_max"),
                "location_raw": x.get("location") or x.get("location_raw"),
                "location_city": (x.get("location_normalized") or {}).get("city") or x.get("location_city"),
                "source": x.get("source"),
                "source_url": x.get("detail_url") or x.get("source_url"),
                "source_type": x.get("source_type"),
                "publish_date": x.get("publish_date"),
                "crawl_time": x.get("crawl_time"),
            })
        return {"total": total, "page": page, "page_size": page_size, "items": norm, "from": "sample"}

    total = len(all_jobs)
    start = (page-1)*page_size
    items = all_jobs[start:start+page_size]
    return {"total": total, "page": page, "page_size": page_size, "items": [_job_to_dict(j) for j in items], "from": "db"}

@router.get("/{job_id}")
def get_job(job_id: str, db: Session = Depends(get_db)):
    j = db.query(Job).filter(Job.id == job_id).first()
    if j:
        return _job_to_dict(j)
    # 尝试样本
    samples = _load_samples()
    for s in samples:
        if (s.get("hash")==job_id or s.get("detail_url","").endswith(job_id) or s.get("id")==job_id):
            return s
    raise HTTPException(status_code=404, detail="Job not found")
