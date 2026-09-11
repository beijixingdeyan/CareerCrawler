from fastapi import APIRouter, Query, BackgroundTasks
from typing import Optional
import json, pathlib, time, requests
from bs4 import BeautifulSoup

router = APIRouter(prefix="/api/jobfairs", tags=["jobfairs"])

BASE = "https://jy.hnust.edu.cn"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def _load():
    for p in [pathlib.Path("data/real/jobfairs.json"), pathlib.Path("data/samples/jobfair_30003.json")]:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return [data]
                return data
            except:
                pass
    return []

def _load_fair(fair_id: str):
    for p in [pathlib.Path(f"data/real/fair_{fair_id}.json"), pathlib.Path(f"data/real/fair30003_64.json") if fair_id=="30003" else None, pathlib.Path(f"data/samples/fair_{fair_id}.json")]:
        if p and p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except:
                pass
    return None

def fetch_fair_companies_raw(fair_id: str):
    # is_total
    r = requests.get(f"{BASE}/module/list_jobfair_company?is_total=1&type=0&fair_id={fair_id}", headers=H, timeout=15)
    try:
        total = int(r.text.strip())
    except:
        total = 0
    if total == 0:
        return []
    # fetch all with count=64
    all_items = []
    # use count=64 to get all in one page if total<=64, else paginate
    count = 64 if total <= 64 else 50
    pages = (total + count - 1)//count
    for page in range(1, pages+1):
        start = (page-1)*count + 1
        url = f"{BASE}/module/list_jobfair_company?is_total=0&start_page={page}&type=0&fair_id={fair_id}&count={count}&start={start}&_={int(time.time()*1000)}"
        rr = requests.get(url, headers=H, timeout=15)
        rr.encoding = "utf-8"
        j = rr.json()
        data = j.get("data", [])
        all_items.extend(data)
        time.sleep(0.35)
        if len(data) == 0:
            break
    return all_items

def enrich_one(c):
    pid = c.get("publish_id")
    cid = c.get("company_id")
    job_detail = {}
    comp_detail = {}
    if pid:
        try:
            url = f"{BASE}/detail/job?id={pid}"
            rr = requests.get(url, headers=H, timeout=15)
            rr.encoding = "utf-8"
            soup = BeautifulSoup(rr.text, "lxml")
            welfare = [w.get_text(strip=True) for w in soup.select(".job-welfare")]
            sections = {}
            for mod in soup.select(".detail-module"):
                tit = mod.select_one(".dm-tit")
                if tit:
                    title = tit.get_text(strip=True)
                    cont = mod.get_text(separator="\n", strip=True).replace(title,"",1).strip()
                    sections[title] = cont[:3000]
            job_detail = {
                "publish_id": pid,
                "detail_url": url,
                "company_name": soup.select_one(".company-name").get_text(strip=True) if soup.select_one(".company-name") else c.get("company_name"),
                "job_name": soup.select_one(".job-name").get_text(strip=True) if soup.select_one(".job-name") else c.get("job_name"),
                "benefits_raw": welfare,
                "benefits_parsed": [b.split("：",1)[1] if "：" in b else b for b in welfare],
                "sections": sections,
            }
            time.sleep(0.2)
        except Exception as e:
            job_detail = {"publish_id": pid, "error": str(e)}
    if cid:
        try:
            url = f"{BASE}/detail/company?id={cid}"
            rr = requests.get(url, headers=H, timeout=15)
            rr.encoding = "utf-8"
            soup = BeautifulSoup(rr.text, "lxml")
            text = soup.get_text(separator="\n", strip=True)
            intro = ""
            if "企业简介" in text:
                idx = text.index("企业简介")
                intro = text[idx:idx+2000]
            comp_detail = {"company_id": cid, "detail_url": url, "intro_excerpt": intro[:2000], "full_text_excerpt": text[:4000]}
            time.sleep(0.2)
        except Exception as e:
            comp_detail = {"company_id": cid, "error": str(e)}
    # merge
    benefits = job_detail.get("benefits_parsed", [])
    return {
        "fair_id": str(c.get("fair_id") or ""),
        "company_name": c.get("company_name"),
        "company_id": cid,
        "company_property": c.get("company_property"),
        "industry_category": c.get("industry_category"),
        "scale": c.get("scale"),
        "city_name": c.get("city_name"),
        "logo_url": c.get("logo_url"),
        "publish_id": pid,
        "job_name": c.get("job_name"),
        "salary": c.get("salary"),
        "degree_require": c.get("degree_require"),
        "job_number": c.get("job_number"),
        "about_major": c.get("about_major"),
        "view_count": c.get("view_count"),
        "job_detail": job_detail,
        "company_detail": comp_detail,
        "benefits": benefits,
        "requirements": job_detail.get("sections",{}).get("岗位要求") or job_detail.get("sections",{}).get("职位要求") or "",
        "description": job_detail.get("sections",{}).get("职位描述") or "",
        "raw": c,
    }

@router.get("")
def list_jobfairs(q: Optional[str]=None, page: int=Query(1, ge=1), page_size: int=Query(15, ge=1, le=50)):
    data=_load()
    filtered=data
    if q:
        ql=q.lower()
        filtered=[x for x in filtered if ql in (x.get("title","")+x.get("address","")+str(x.get("fair_id",""))).lower()]
    total=len(filtered)
    start=(page-1)*page_size
    return {"total": total, "page": page, "page_size": page_size, "items": filtered[start:start+page_size]}

@router.get("/stats")
def stats():
    data=_load()
    # count cached fairs
    cached = list(pathlib.Path("data/real").glob("fair_*.json"))
    return {"total": len(data), "cached_fairs": len(cached), "fair30003_raw": 64}

# 必须放在 /{fair_id} 之前，避免 30003 被当作 fair_id
@router.get("/30003/companies")
def fair_30003_companies():
    data = _load_fair("30003")
    if data is None:
        # fallback to raw fetch
        raw = fetch_fair_companies_raw("30003")
        return {"fair_id":"30003","title":"湖南科技大学2027届计算机类毕业生专场招聘会","total": len(raw), "companies": raw, "source": f"{BASE}/module/list_jobfair_company?fair_id=30003", "note": "raw list, enriched available via /30003/companies?enrich=1"}
    return {"fair_id":"30003","title":"湖南科技大学2027届计算机类毕业生专场招聘会","total": len(data), "companies": data, "source": f"{BASE}/module/list_jobfair_company?fair_id=30003"}

@router.get("/{fair_id}/companies")
def fair_companies(fair_id: str, enrich: int = Query(0, ge=0, le=1), refresh: int = Query(0, ge=0, le=1)):
    # 缓存路径
    cache_path = pathlib.Path(f"data/real/fair_{fair_id}.json")
    # 特殊 30003 直接用已富化的 64 份
    if fair_id=="30003" and cache_path.exists() is False and pathlib.Path("data/real/fair30003_64.json").exists():
        # 兼容旧命名
        import shutil; shutil.copy("data/real/fair30003_64.json", str(cache_path))
    if cache_path.exists() and refresh==0 and enrich==1:
        # 已富化则直接返回
        try:
            data=json.loads(cache_path.read_text(encoding="utf-8"))
            # 判断是否已富化（有 job_detail）
            if data and isinstance(data[0], dict) and "job_detail" in data[0]:
                return {"fair_id": fair_id, "total": len(data), "companies": data, "source": f"{BASE}/module/list_jobfair_company?fair_id={fair_id}", "cached": True, "enriched": True}
        except:
            pass
    if enrich==0:
        # 仅 raw 列表，快速
        cached_raw = pathlib.Path(f"data/real/fair_{fair_id}_raw.json")
        if cached_raw.exists() and refresh==0:
            try:
                raw=json.loads(cached_raw.read_text(encoding="utf-8"))
                return {"fair_id": fair_id, "total": len(raw), "companies": raw, "source": f"{BASE}/module/list_jobfair_company?fair_id={fair_id}", "cached": True, "enriched": False}
            except:
                pass
        raw = fetch_fair_companies_raw(fair_id)
        # 缓存 raw
        try:
            pathlib.Path("data/real").mkdir(parents=True, exist_ok=True)
            pathlib.Path(f"data/real/fair_{fair_id}_raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
        except:
            pass
        return {"fair_id": fair_id, "total": len(raw), "companies": raw, "source": f"{BASE}/module/list_jobfair_company?fair_id={fair_id}", "cached": False, "enriched": False}
    else:
        # 富化：raw -> 逐家抓 detail
        raw = fetch_fair_companies_raw(fair_id)
        enriched=[]
        for c in raw:
            enriched.append(enrich_one(c))
        # 缓存富化
        try:
            cache_path.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
        except:
            pass
        return {"fair_id": fair_id, "total": len(enriched), "companies": enriched, "source": f"{BASE}/module/list_jobfair_company?fair_id={fair_id}", "cached": False, "enriched": True}

@router.get("/{fair_id}")
def get_one(fair_id: str):
    data=_load()
    for x in data:
        if str(x.get("fair_id"))==fair_id or str(x.get("id"))==fair_id or str(x.get("fair_id"))==str(fair_id):
            return x
    return {"error": "not found", "fair_id": fair_id}
