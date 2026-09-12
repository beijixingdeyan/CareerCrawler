from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
import json, pathlib
from ..database import get_db
from ..models import Job

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# 辅助：若 DB 为空，尝试从 data/real 真实数据加载
SAMPLE_PATHS = [
    pathlib.Path("data/real/jobs.json"),
    pathlib.Path("data/real/careers.json"),
    pathlib.Path("data/samples/crawl_latest.json"),
    pathlib.Path("../data/samples/crawl_latest.json"),
    pathlib.Path("data/samples/hnust_sample.json"),
]

def _is_expired(item: dict) -> bool:
    import datetime
    # 1) overdue 标记
    raw_inner = item.get("raw") or {}
    if raw_inner.get("overdue") is True:
        return True
    # 2) publish_time 超 14 天即视为失效（仅保留近2周，过滤失效链接）
    raw = item.get("publish_time") or item.get("publish_date") or item.get("meet_day") or ""
    if raw:
        try:
            dt = datetime.datetime.fromisoformat(str(raw).split(" ")[0])
            today = datetime.datetime(2026, 9, 12)
            cutoff = today - datetime.timedelta(days=14)
            if dt < cutoff:
                return True
        except:
            pass
    # 3) end_time 已过也视为失效
    end = raw_inner.get("end_time") or item.get("end_time") or item.get("deadline") or ""
    if end:
        try:
            dt = datetime.datetime.fromisoformat(str(end).split(" ")[0])
            today = datetime.datetime(2026, 9, 12)
            return dt < today
        except:
            pass
    return False

def _load_samples():
    for p in SAMPLE_PATHS:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                # 直接在这里不过滤，留给调用方按需过滤
                return data
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
    # 过滤失效
    all_jobs = [j for j in all_jobs if not _is_expired({"publish_time": j.publish_date or j.crawl_time})]
    if skill:
        all_jobs = [j for j in all_jobs if any(s.get("name") == skill for s in (j.skills or []))]

    # 若 DB 为空，返回样本
    if not all_jobs:
        samples = _load_samples()
        # 先过滤失效招聘（publish_time < 30 天前，及 overdue/end_time 已过期）
        samples = [x for x in samples if not _is_expired(x)]
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
        # 适配字段（兼容真实 API 的多字段：careers 的 meet_name，jobs 的 job_name 等）
        norm = []
        for x in items:
            # 真实数据可能使用不同字段名，统一映射
            title = x.get("title") or x.get("job_name") or x.get("meet_name")
            comp = x.get("company_name")
            loc_city = x.get("location_city") or x.get("city_name") or x.get("job_city") or (x.get("location_normalized") or {}).get("city")
            loc_raw = x.get("location") or x.get("location_raw") or x.get("address") or loc_city
            sal_raw = x.get("salary_raw") or x.get("salary") or (x.get("salary_parsed") or {}).get("raw")
            smin = x.get("salary_min")
            smax = x.get("salary_max")
            # 尝试从 salary 字符串解析如 "5K-7K/月"
            if not smin and sal_raw:
                import re
                m = re.search(r"(\d+(?:\.\d+)?)\s*[Kk]\s*[-~至]+\s*(\d+(?:\.\d+)?)\s*[Kk]", sal_raw)
                if m:
                    smin = int(float(m.group(1))*1000)
                    smax = int(float(m.group(2))*1000)
            norm.append({
                "id": x.get("hash") or x.get("id") or x.get("publish_id") or x.get("career_talk_id") or x.get("fair_id") or x.get("detail_url","")[-12:] or str(hash(title))[-8:],
                "title": title,
                "company_name": comp,
                "category": x.get("category") or x.get("industry_category") or "其他",
                "job_type": x.get("source_type") or ("careers" if x.get("career_talk_id") else "jobs"),
                "description": x.get("description") or x.get("about_major") or x.get("professionals") or "",
                "skills": x.get("skills") or [],
                "salary_raw": sal_raw,
                "salary_min": (x.get("salary_parsed") or {}).get("min") or smin,
                "salary_max": (x.get("salary_parsed") or {}).get("max") or smax,
                "location_raw": loc_raw,
                "location_city": loc_city,
                "source": x.get("source") or "hnust",
                "source_url": x.get("detail_url") or x.get("source_url"),
                "source_type": x.get("source_type") or ("careers" if x.get("career_talk_id") else "jobs"),
                "publish_date": x.get("publish_date") or x.get("publish_time") or x.get("meet_day"),
                "crawl_time": x.get("crawl_time"),
            })
        src = "real" if any("data/real" in str(p) for p in SAMPLE_PATHS if p.exists()) else "sample"
        return {"total": total, "page": page, "page_size": page_size, "items": norm, "from": src}

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
