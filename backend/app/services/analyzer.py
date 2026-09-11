from collections import Counter, defaultdict
from typing import List, Dict
import re

def salary_stats(jobs: List[dict]) -> dict:
    vals = []
    for j in jobs:
        if j.get("salary_min") and j.get("salary_max"):
            vals.append((j["salary_min"] + j["salary_max"]) / 2)
        elif j.get("salary_min"):
            vals.append(j["salary_min"])
    if not vals:
        return {"avg": None, "min": None, "max": None, "count": 0}
    return {
        "avg": round(sum(vals)/len(vals)),
        "min": min(vals),
        "max": max(vals),
        "count": len(vals),
        "distribution": Counter([ f"{int(v//1000)}k" for v in vals])
    }

def industry_distribution(jobs: List[dict]) -> dict:
    c = Counter([j.get("category") or "其他" for j in jobs])
    return dict(c.most_common())

def skill_ranking(jobs: List[dict], top_n=15) -> List[dict]:
    cnt = Counter()
    for j in jobs:
        for s in (j.get("skills") or []):
            cnt[s["name"]] += 1
    return [{"skill": k, "count": v} for k, v in cnt.most_common(top_n)]

def location_distribution(jobs: List[dict]) -> dict:
    c = Counter([ (j.get("location_city") or j.get("location_raw") or "未知") for j in jobs])
    return dict(c.most_common(10))

def trend_by_date(jobs: List[dict]) -> List[dict]:
    # 按 publish_date 聚合
    bucket = Counter()
    for j in jobs:
        d = (j.get("publish_date") or j.get("crawl_time") or "")[:10]
        if d:
            bucket[d] += 1
    # 排序
    items = sorted(bucket.items())
    return [{"date": k, "count": v} for k, v in items[-30:]]

def dashboard(jobs: List[dict], companies: List[dict]) -> dict:
    today = None
    # 简化：取最近一天为 today
    trend = trend_by_date(jobs)
    today_count = trend[-1]["count"] if trend else 0
    sal = salary_stats(jobs)
    return {
        "total_jobs": len(jobs),
        "total_companies": len(companies) if companies else len(set(j["company_name"] for j in jobs)),
        "today_new": today_count,
        "avg_salary": sal["avg"],
        "industry_dist": industry_distribution(jobs),
        "skill_rank": skill_ranking(jobs),
        "salary_stats": sal,
        "location_dist": location_distribution(jobs),
        "trend": trend,
    }
