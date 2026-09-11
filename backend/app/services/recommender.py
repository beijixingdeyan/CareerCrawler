from typing import List, Dict

SKILL_ALIASES = {
    "js": "javascript", "ts": "typescript", "py": "python"
}

def normalize(s: str) -> str:
    return s.strip().lower()

def recommend_for_user(user: dict, jobs: List[dict], limit=20) -> List[dict]:
    """
    简易内容推荐：基于用户技能、偏好城市、偏好类别
    """
    user_skills = set(normalize(x["name"]) if isinstance(x, dict) else normalize(str(x)) for x in (user.get("skills") or []))
    pref_cities = set(normalize(c) for c in (user.get("preferred_cities") or []))
    pref_cats = set(normalize(c) for c in (user.get("preferred_categories") or []))

    scored = []
    for j in jobs:
        score = 0.0
        # 技能匹配
        job_skills = set(normalize(s["name"]) for s in (j.get("skills") or []))
        if job_skills and user_skills:
            inter = len(job_skills & user_skills)
            union = len(job_skills | user_skills)
            jaccard = inter / union if union else 0
            score += jaccard * 0.55
            # 完全命中加分
            score += (inter * 0.04)

        # 类别偏好
        cat = normalize(j.get("category") or "")
        if cat in pref_cats:
            score += 0.16
        # 城市偏好
        city = normalize(j.get("location_city") or j.get("location_raw") or "")
        if any(pc in city for pc in pref_cities):
            score += 0.14
        # 薪资（有明确定价的加分）
        if j.get("salary_min"):
            score += 0.05
        # 热门度（模拟：发布时间越新越高）
        # 保持稳定
        scored.append((score, j))

    scored.sort(key=lambda x: x[0], reverse=True)
    # 去重按公司+标题
    seen = set()
    out = []
    for s, j in scored:
        key = (j["company_name"], j["title"])
        if key in seen:
            continue
        seen.add(key)
        out.append({**j, "_score": round(s, 3)})
        if len(out) >= limit:
            break
    return out

def explain_recommendation(user: dict, job: dict) -> List[str]:
    reasons = []
    user_skills = set(normalize(x["name"]) if isinstance(x, dict) else normalize(str(x)) for x in (user.get("skills") or []))
    job_skills = set(normalize(s["name"]) for s in (job.get("skills") or []))
    inter = user_skills & job_skills
    if inter:
        reasons.append(f"技能匹配：{', '.join(list(inter)[:4])}")
    if normalize(job.get("category") or "") in set(normalize(c) for c in (user.get("preferred_categories") or [])):
        reasons.append(f"类别偏好：{job.get('category')}")
    city = job.get("location_city") or job.get("location_raw") or ""
    if any(normalize(c) in normalize(city) for c in (user.get("preferred_cities") or [])):
        reasons.append(f"地点匹配：{city}")
    if job.get("salary_min"):
        reasons.append(f"薪资：{job.get('salary_min')}-{job.get('salary_max')}")
    if not reasons:
        reasons.append("综合热度推荐")
    return reasons
