"""
CareerCrawler - HNUST 就业网爬虫引擎
支持：宣讲会 / 招聘公告 / 双选会 / 实习岗位
适配 bysjy 体系的湖南科技大学就业网 jy.hnust.edu.cn
策略：requests + BeautifulSoup 主路径，Playwright 兜底渲染，反爬中间件，增量去重
"""
from __future__ import annotations
import re
import json
import time
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup

# --------------------------- 配置 ---------------------------
HNUST_BASE = "https://jy.hnust.edu.cn"
HNUST_TOKEN = "yxqqnn0000000006"  # 学校 token（公开，来自页面 HTML）

# bysjy 真实数据接口通过 HTML 页面异步加载，直接爬列表页 + 详情页更稳
# 列表页示例：
#   /module/careers  宣讲会
#   /module/jobfairs 双选会
#   /module/jobs?is_practice=0 正式岗
#   /module/jobs?is_practice=1 实习

TARGETS = [
    {
        "name": "careers",
        "label": "校内宣讲会",
        "url": f"{HNUST_BASE}/module/careers",
        "paginated": True,
        "detail_prefix": "/detail/career?id=",
    },
    {
        "name": "jobfairs",
        "label": "双选会",
        "url": f"{HNUST_BASE}/module/jobfairs",
        "paginated": True,
        "detail_prefix": "/detail/jobfair?id=",
    },
    {
        "name": "jobs_official",
        "label": "正式岗位",
        "url": f"{HNUST_BASE}/module/jobs?is_practice=0",
        "paginated": True,
        "detail_prefix": "/detail/job?id=",
    },
    {
        "name": "jobs_intern",
        "label": "实习岗位",
        "url": f"{HNUST_BASE}/module/jobs?is_practice=1",
        "paginated": True,
        "detail_prefix": "/detail/job?id=",
    },
    {
        "name": "news",
        "label": "就业公告",
        "url": f"{HNUST_BASE}/module/news?type_id=1727&menu_id=3283",
        "paginated": True,
        "detail_prefix": "/detail/news?id=",
    },
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

SKILL_KEYWORDS = {
    "编程语言": ["Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust", "PHP", "Kotlin", "Swift"],
    "前端": ["React", "Vue", "Angular", "HTML", "CSS", "Webpack", "Vite", "Next.js", "UniApp"],
    "后端": ["Spring", "SpringBoot", "Django", "Flask", "FastAPI", "Node.js", "Express", "MyBatis"],
    "数据库": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Oracle", "SQLite"],
    "AI/ML": ["TensorFlow", "PyTorch", "机器学习", "深度学习", "NLP", "CV", "大模型", "LLM", "AIGC"],
    "大数据": ["Hadoop", "Spark", "Flink", "Hive", "Kafka", "大数据"],
    "运维/云": ["Docker", "Kubernetes", "Linux", "AWS", "阿里云", "Nginx", "CI/CD", "Jenkins"],
    "安全": ["渗透测试", "漏洞", "逆向", "密码学", "安全", "CTF"],
    "嵌入式/物联网": ["STM32", "单片机", "嵌入式", "物联网", "MQTT", "ARM"],
    "工具": ["Git", "Jira", "Confluence", "Axure", "Figma"],
}

CATEGORY_KEYWORDS = {
    "技术开发": ["开发", "工程师", "程序", "技术", "算法", "架构", "研发", "后端", "前端", "全栈", "运维", "测试"],
    "产品设计": ["产品", "设计", "UI", "UX", "交互", "视觉"],
    "运营市场": ["运营", "市场", "推广", "营销", "品牌", "内容"],
    "销售商务": ["销售", "商务", "客户", "渠道", "BD"],
    "职能支持": ["人力", "人事", "财务", "行政", "法务", "采购", "文员"],
    "金融分析": ["金融", "投资", "分析", "风控", "量化", "证券"],
    "安全类": ["安全", "渗透", "攻防", "漏洞"],
}

# --------------------------- 工具函数 ---------------------------

def parse_salary(salary_text: str) -> dict:
    if not salary_text:
        return {"type": "unknown", "raw": salary_text}
    t = salary_text.strip()
    pat = [
        (r"(\d+(?:\.\d+)?)\s*[kK]\s*[-~至]+\s*(\d+(?:\.\d+)?)\s*[kK]", lambda m: {"min": int(float(m.group(1))*1000), "max": int(float(m.group(2))*1000)}),
        (r"(\d+(?:\.\d+)?)\s*[-~至]+\s*(\d+(?:\.\d+)?)\s*[kK]", lambda m: {"min": int(float(m.group(1))*1000), "max": int(float(m.group(2))*1000)}),
        (r"(\d+)\s*[-~至]+\s*(\d+)\s*(?:元/月|/月|每月)?", lambda m: {"min": int(m.group(1)), "max": int(m.group(2))}),
        (r"年薪\s*(\d+(?:\.\d+)?)\s*[万wW]\s*[-~至]+\s*(\d+(?:\.\d+)?)\s*[万wW]", lambda m: {"min": int(float(m.group(1))*10000/12), "max": int(float(m.group(2))*10000/12)}),
        (r"(\d+(?:\.\d+)?)\s*[万wW]/年", lambda m: {"min": int(float(m.group(1))*10000/12), "max": int(float(m.group(1))*10000/12)}),
    ]
    for p, fn in pat:
        m = re.search(p, t)
        if m:
            r2 = fn(m)
            r2.update({"unit": "month", "currency": "CNY", "raw": t})
            return r2
    if re.search(r"面议| negotiable |薪资面议", t, re.I):
        return {"type": "negotiable", "raw": t, "unit": "month", "currency": "CNY"}
    return {"type": "unknown", "raw": t}

def extract_skills(text: str) -> List[Dict[str, str]]:
    if not text:
        return []
    lower = text.lower()
    found = []
    for cat, skills in SKILL_KEYWORDS.items():
        for s in skills:
            if s.lower() in lower:
                found.append({"name": s, "category": cat})
    # 去重
    uniq = {f"{x['name']}_{x['category']}": x for x in found}
    return list(uniq.values())

def classify_job(title: str, desc: str) -> str:
    t = (title or "" + " " + (desc or "")).lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in t for kw in kws):
            return cat
    return "其他"

def normalize_location(loc: str) -> dict:
    if not loc:
        return {"province": None, "city": None, "district": None, "raw": loc}
    # 简单规则：湘潭/长沙/北京/上海/广州/深圳/杭州 等
    cities = ["北京","上海","广州","深圳","杭州","南京","苏州","武汉","长沙","湘潭","株洲","成都","重庆","西安","合肥","厦门","济南","青岛","天津","宁波","无锡","郑州","南昌","福州","昆明","南宁"]
    province_map = {"湖南":"湖南","北京":"北京","上海":"上海","广东":"广东","浙江":"浙江","江苏":"江苏","湖北":"湖北","四川":"四川"}
    found_city = None
    for c in cities:
        if c in loc:
            found_city = c
            break
    return {"province": "湖南" if found_city in ["长沙","湘潭","株洲"] else None, "city": found_city, "district": None, "raw": loc}

def hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:12]

# --------------------------- 爬虫引擎 ---------------------------

class AntiSpiderSession:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        })

    def get(self, url, **kwargs):
        # 随机延迟 0.8-2.2s
        time.sleep(random.uniform(0.8, 2.2))
        # 轮换 UA
        self.s.headers["User-Agent"] = random.choice(USER_AGENTS)
        resp = self.s.get(url, timeout=15, **kwargs)
        if resp.status_code == 429:
            wait = int(resp.headers.get("Retry-After", "10"))
            time.sleep(wait)
            resp = self.s.get(url, timeout=15, **kwargs)
        # 检测验证码
        if "验证码" in resp.text or "captcha" in resp.text.lower():
            print(f"[WARN] Captcha detected at {url}")
        return resp

@dataclass
class CrawlItem:
    source: str
    source_type: str
    title: str
    company_name: str
    detail_url: str
    publish_date: Optional[str] = None
    meet_time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_raw: Optional[str] = None
    salary_parsed: Optional[dict] = None
    skills: Optional[List[dict]] = None
    category: Optional[str] = None
    crawl_time: str = ""
    hash: str = ""

    def finalize(self):
        self.crawl_time = datetime.now().isoformat()
        self.hash = hash_url(self.detail_url)
        if self.salary_raw:
            self.salary_parsed = parse_salary(self.salary_raw)
        blob = (self.title or "") + " " + (self.description or "") + " " + (self.requirements or "")
        self.skills = extract_skills(blob)
        self.category = classify_job(self.title or "", self.description or "")
        return self

class HnustCrawler:
    def __init__(self, use_playwright: bool = False):
        self.session = AntiSpiderSession()
        self.use_playwright = use_playwright
        self.seen = set()
        self.items: List[CrawlItem] = []

    def _fetch(self, url: str) -> Optional[BeautifulSoup]:
        try:
            # 尝试 requests
            r = self.session.get(url)
            if r.status_code != 200:
                print(f"[ERR] {r.status_code} {url}")
                return None
            # 如果页面明显是 JS 渲染占位且无列表，尝试 playwright
            if self.use_playwright and ("正在加载" in r.text or len(r.text) < 5000):
                return self._fetch_playwright(url)
            return BeautifulSoup(r.text, "lxml")
        except Exception as e:
            print(f"[ERR] fetch {url}: {e}")
            if self.use_playwright:
                try:
                    return self._fetch_playwright(url)
                except Exception as e2:
                    print(f"[ERR] playwright fallback failed: {e2}")
            return None

    def _fetch_playwright(self, url: str) -> BeautifulSoup:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=random.choice(USER_AGENTS))
            page.goto(url, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2500)
            content = page.content()
            browser.close()
            return BeautifulSoup(content, "lxml")

    def parse_list_page(self, target: dict, page_idx: int = 1) -> List[Dict[str, Any]]:
        base_url = target["url"]
        # 分页参数猜测：by soy 常用 ?page= 或 ?currentPage=
        if page_idx == 1:
            url = base_url
        else:
            sep = "&" if "?" in base_url else "?"
            # 尝试多种分页
            url = f"{base_url}{sep}page={page_idx}"
        print(f"[INFO] Fetch list: {target['label']} page {page_idx} -> {url}")
        soup = self._fetch(url)
        if not soup:
            return []
        # 多种选择器兼容
        links = []
        # 1. 标准详情链接
        for a in soup.select(f"a[href*='{target['detail_prefix']}']"):
            href = a.get("href")
            if href:
                full = urljoin(HNUST_BASE, href)
                title = a.get_text(strip=True) or a.get("title") or ""
                if full not in self.seen:
                    links.append({"title": title, "url": full})
        # 2. 列表项兜底：所有 /detail/ 链接
        if not links:
            for a in soup.select("a[href*='/detail/']"):
                href = a.get("href")
                if href and target["detail_prefix"].split("?")[0] in href:
                    full = urljoin(HNUST_BASE, href)
                    if full not in self.seen:
                        links.append({"title": a.get_text(strip=True), "url": full})
        # 去重
        uniq = {}
        for x in links:
            uniq[x["url"]] = x
        result = list(uniq.values())
        print(f"  -> found {len(result)} links")
        return result

    def parse_detail(self, url: str, source_type: str, source_label: str) -> Optional[CrawlItem]:
        if url in self.seen:
            return None
        self.seen.add(url)
        soup = self._fetch(url)
        if not soup:
            return None
        # 通用提取：标题在 h1 / .detail-title / .tit
        title = ""
        for sel in ["h1", ".detail-title", ".tit", ".title", ".info-title"]:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                title = el.get_text(strip=True)
                break
        if not title:
            # fallback: title tag
            title = soup.title.get_text(strip=True) if soup.title else url

        # 公司名
        company = ""
        for sel in [".company", ".com-name", ".detail-company", ".company-name"]:
            el = soup.select_one(sel)
            if el:
                company = el.get_text(strip=True)
                break
        if not company:
            # 从标题中提取 “- 公司” 或 “公司：”
            m = re.search(r"[—-]\s*([\u4e00-\u9fa5A-Za-z0-9（）()]+公司)", title)
            if m:
                company = m.group(1)

        # 时间 / 地点
        meet_time = None
        location = None
        text_all = soup.get_text(separator="\n")
        m_time = re.search(r"(\d{4}[-年/]\d{1,2}[-月/]\d{1,2}\s*\d{1,2}:\d{2})", text_all)
        if m_time:
            meet_time = m_time.group(1)
        # 地点关键词
        m_loc = re.search(r"(湖南科技大学[^\n]{0,30}|敏行楼[^\n]{0,30}|立德楼[^\n]{0,30}|招聘大厅[^\n]{0,20})", text_all)
        if m_loc:
            location = m_loc.group(1).strip()

        # 描述与要求：取主要内容区
        desc = ""
        req = ""
        content_selectors = [".detail-content", ".content", ".article-content", ".info-content", "#content", ".main-content"]
        main = None
        for sel in content_selectors:
            el = soup.select_one(sel)
            if el and len(el.get_text(strip=True)) > 50:
                main = el
                break
        if main:
            # 提取所有 p、li
            desc = "\n".join([p.get_text(strip=True) for p in main.select("p,li") if p.get_text(strip=True)])
            if not desc:
                desc = main.get_text(separator="\n", strip=True)[:3000]
        else:
            desc = text_all[:3000]

        # 薪资（招聘详情中）
        salary_raw = None
        m_sal = re.search(r"(?:薪资|工资|待遇|月薪|年薪)[：: ]*([^\n]{0,30})", text_all)
        if m_sal:
            cand = m_sal.group(1).strip()[:30]
            if re.search(r"\d", cand) or "面议" in cand:
                salary_raw = cand

        # 发布日期
        publish_date = None
        m_date = re.search(r"(\d{4}-\d{2}-\d{2})", text_all)
        if m_date:
            publish_date = m_date.group(1)

        item = CrawlItem(
            source=source_label,
            source_type=source_type,
            title=title[:120],
            company_name=company[:80] or "未知企业",
            detail_url=url,
            publish_date=publish_date,
            meet_time=meet_time,
            location=location,
            description=desc[:4000],
            requirements=req or desc[:2000],
            salary_raw=salary_raw,
        ).finalize()
        return item

    def crawl_target(self, target: dict, max_pages: int = 3, max_items: int = 30) -> List[CrawlItem]:
        collected: List[CrawlItem] = []
        for page in range(1, max_pages+1):
            links = self.parse_list_page(target, page)
            if not links:
                break
            for lk in links:
                if len(collected) >= max_items:
                    break
                it = self.parse_detail(lk["url"], target["name"], target["label"])
                if it:
                    collected.append(it)
                    print(f"  + {it.title[:40]} | {it.company_name} | {it.detail_url}")
                time.sleep(random.uniform(0.4, 1.0))
            if len(collected) >= max_items:
                break
            # 如果本页不足，认为末页
            if len(links) < 8:
                break
        return collected

    def crawl_all(self, max_pages: int = 2, per_target_limit: int = 20) -> List[Dict[str, Any]]:
        all_items: List[CrawlItem] = []
        for tgt in TARGETS:
            try:
                items = self.crawl_target(tgt, max_pages=max_pages, max_items=per_target_limit)
                all_items.extend(items)
            except Exception as e:
                print(f"[ERR] target {tgt['name']}: {e}")
        # 去重按 hash
        uniq = {}
        for it in all_items:
            uniq[it.hash] = it
        result = [asdict(v) for v in uniq.values()]
        # 按发布时间倒序
        result.sort(key=lambda x: x.get("publish_date") or x.get("crawl_time") or "", reverse=True)
        return result

    def crawl_jobfair_detail(self, jobfair_id: str = "30003") -> Dict[str, Any]:
        """专项：抓取指定双选会详情（用于计科专场）"""
        url = f"{HNUST_BASE}/detail/jobfair?id={jobfair_id}"
        soup = self._fetch(url)
        if not soup:
            return {"error": "fetch failed", "url": url}
        text = soup.get_text(separator="\n")
        # 提取参会单位（现场招聘 / 网络招聘 区块）
        companies = []
        for a in soup.select("a[href*='/detail/com']"):
            companies.append({"name": a.get_text(strip=True), "url": urljoin(HNUST_BASE, a.get("href"))})
        # 兜底：从文本中提取公司列表（若 JS 渲染未命中，返回空列表并提示）
        title_el = soup.select_one("h1") or soup.select_one(".detail-title")
        title = title_el.get_text(strip=True) if title_el else f"双选会 {jobfair_id}"
        return {
            "id": jobfair_id,
            "title": title,
            "url": url,
            "raw_text_excerpt": text[:6000],
            "companies_hint": companies[:30],
            "crawl_time": datetime.now().isoformat(),
            "note": "参会单位需登录后通过接口获取，此处为静态可得信息；完整名单可通过现场爬取或校方公布名单补充",
        }


def main():
    import argparse, pathlib
    parser = argparse.ArgumentParser(description="HNUST Career Crawler")
    parser.add_argument("--pages", type=int, default=2, help="每类目爬取页数")
    parser.add_argument("--limit", type=int, default=20, help="每类目上限")
    parser.add_argument("--playwright", action="store_true", help="启用 playwright 兜底")
    parser.add_argument("--out", type=str, default="data/samples/crawl_latest.json", help="输出路径")
    parser.add_argument("--jobfair", type=str, default="", help="只爬指定双选会 id")
    args = parser.parse_args()

    crawler = HnustCrawler(use_playwright=args.playwright)
    if args.jobfair:
        data = crawler.crawl_jobfair_detail(args.jobfair)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        pathlib.Path("data/samples/jobfair_%s.json" % args.jobfair).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    result = crawler.crawl_all(max_pages=args.pages, per_target_limit=args.limit)
    print(f"[DONE] total {len(result)} items")
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved to {out}")

if __name__ == "__main__":
    main()
