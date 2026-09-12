from collections import Counter, defaultdict
from typing import List, Dict
import re

def _norm_salary(v):
    if v is None:
        return None
    try:
        v = float(v)
        # 如果是 1-100 的小数值，实际是 K，需要 *1000
        if v < 1000 and v > 0:
            return v * 1000
        return v
    except:
        return None

def salary_stats(jobs: List[dict]) -> dict:
    vals = []
    for j in jobs:
        smin = _norm_salary(j.get("salary_min"))
        smax = _norm_salary(j.get("salary_max"))
        # 尝试从 salary_raw 解析如 "5K-7K"
        if (smin is None or smax is None) and j.get("salary_raw"):
            m = re.search(r"(\d+(?:\.\d+)?)\s*[Kk]\s*[-~至]+\s*(\d+(?:\.\d+)?)\s*[Kk]", j["salary_raw"])
            if m:
                smin = float(m.group(1))*1000
                smax = float(m.group(2))*1000
        if smin and smax:
            vals.append((smin + smax) / 2)
        elif smin:
            vals.append(smin)
        elif smax:
            vals.append(smax)
    if not vals:
        return {"avg": None, "min": None, "max": None, "count": 0, "distribution": {}}
    return {
        "avg": round(sum(vals)/len(vals)),
        "min": int(min(vals)),
        "max": int(max(vals)),
        "count": len(vals),
        "distribution": dict(Counter([ f"{int(v//1000)}k" for v in vals]))
    }

def industry_distribution(jobs: List[dict], top_n: int = 17) -> dict:
    KNOWN = {"制造业","教育","信息传输、软件和信息技术服务业","建筑业","批发和零售业","电力、热力、燃气及水生产和供应业","采矿业","科学研究和技术服务业","交通运输、仓储和邮政业","农、林、牧、渔业","住宿和餐饮业","文化、体育和娱乐业","金融业","水利、环境和公共设施管理业","公共管理、社会保障和社会组织","租赁和商务服务业"}
    def _norm(ind):
        if not ind: return "其它"
        if ind in KNOWN: return ind
        # 模糊：若包含关键词则归到已知，否则其它
        for k in KNOWN:
            if k in ind or ind in k:
                return k
        return "其它"
    c = Counter([_norm(j.get("industry") or j.get("industry_category") or j.get("category") or "") for j in jobs])
    return dict(c.most_common(top_n))

SKILL_KEYWORDS = ["Java","Python","C++","Go","JavaScript","TypeScript","Vue","React","SpringBoot","Spring","MySQL","Redis","Docker","Kubernetes","Linux","机器学习","深度学习","算法","大数据","Hadoop","Spark","Flink","Android","iOS","前端","后端","测试","运维","网络安全","渗透","C#","Node.js","Django","Flask","TensorFlow","PyTorch"]

def skill_ranking(jobs: List[dict], top_n=15) -> List[dict]:
    cnt = Counter()
    for j in jobs:
        # 1. 已标注的 skills
        for s in (j.get("skills") or []):
            name = s.get("name") if isinstance(s, dict) else str(s)
            if name: cnt[name] += 1
        # 2. 从标题/描述/要求中关键词提取
        text = " ".join([str(j.get("title","")), str(j.get("description","")), str(j.get("requirements","")), str(j.get("category",""))])
        for kw in SKILL_KEYWORDS:
            if kw.lower() in text.lower():
                cnt[kw] += 1
        # 3. 从 category 提取
        cat = j.get("category") or ""
        if cat and cat != "其他":
            cnt[cat] += 1
    # 过滤太短的
    filtered = [(k,v) for k,v in cnt.items() if len(k)>=2]
    return [{"skill": k, "count": v} for k, v in Counter(dict(filtered)).most_common(top_n)]

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
