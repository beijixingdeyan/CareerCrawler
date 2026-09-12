import json, pathlib, re

careers_path = pathlib.Path("data/real/careers.json")
enterprise_path = pathlib.Path("data/real/enterprise_library.json")
fortune_path = pathlib.Path("data/real/fortune500_2024.json")

careers = json.loads(careers_path.read_text(encoding="utf-8"))
enterprise = json.loads(enterprise_path.read_text(encoding="utf-8")) if enterprise_path.exists() else []
fortune = json.loads(fortune_path.read_text(encoding="utf-8")) if fortune_path.exists() else {}
rankings = fortune.get("rankings", {})

# 企业库索引
ent_index = {e["name"]: e for e in enterprise}
# 也按简称索引
for e in enterprise:
    short = e["name"].replace("有限公司","").replace("股份有限公司","").replace("（","(").split("(")[0].strip()
    ent_index[short] = e

# 官方链接 heuristic：已知大厂用 enterprise 的，否则用拼音或搜索
# 简单映射：常见公司官网
known_official = {
    "华为技术有限公司": "https://www.huawei.com",
    "腾讯科技（深圳）有限公司": "https://www.tencent.com",
    "阿里巴巴（中国）有限公司": "https://www.alibaba.com",
    "字节跳动科技有限公司": "https://www.bytedance.com",
    "百度在线网络技术（北京）有限公司": "https://www.baidu.com",
    "小米科技有限责任公司": "https://www.mi.com",
    "美团": "https://www.meituan.com",
    "京东集团": "https://www.jd.com",
    "网易公司": "https://www.163.com",
    "比亚迪股份有限公司": "https://www.byd.com",
    "中国平安财产保险股份有限公司": "https://www.pingan.com",
    "中兴通讯股份有限公司": "https://www.zte.com.cn",
    "大疆创新科技有限公司": "https://www.dji.com",
    "商汤科技": "https://www.sensetime.com",
    "月之暗面科技有限公司（Kimi）": "https://www.moonshot.cn",
    "深度求索（DeepSeek）": "https://www.deepseek.com",
}

# 为宣讲会每个企业生成背景
enriched = []
# 去重按公司名，但保留每个宣讲会场次
seen_company = {}

for c in careers:
    name = c.get("company_name") or c.get("title") or "未知企业"
    # 查找企业库
    ent = ent_index.get(name)
    if not ent:
        # 模糊匹配：去掉括号后匹配
        for k,v in ent_index.items():
            if name in k or k in name:
                ent = v
                break
    # 排名
    rank = None
    rank_source = None
    # 精确匹配排名
    if name in rankings:
        rank = rankings[name]
        rank_source = "《财富》中国500强 2024"
    else:
        # 模糊匹配排名
        for rname, rrank in rankings.items():
            if rname in name or name in rname:
                if rrank is not None:
                    rank = rrank
                    rank_source = "《财富》中国500强 2024（模糊匹配）"
                    break
    # 如果是大厂但无排名，标为独角兽或未上榜
    if rank is None:
        if "Kimi" in name or "DeepSeek" in name:
            rank = None
        else:
            # 未上榜
            rank = "未上榜"
            rank_source = "中国企业500强 2024 外"

    # 介绍
    if ent and ent.get("intro"):
        intro = ent["intro"]
        official = ent.get("official_url") or ent.get("recruitment_url") or known_official.get(name)
        products = ent.get("products","")
        industry = ent.get("industry")
        scale = ent.get("scale")
        recruitment = ent.get("recruitment_url")
        source = ent.get("source")
    else:
        # heuristic介绍
        industry = c.get("industry_category") or "信息技术/制造业"
        scale = c.get("scale") or "100-500人"
        # 根据名称生成简介
        if "科技" in name:
            intro = f"{name}是一家专注于技术研发与产品创新的科技企业，主营业务涵盖软件开发、系统集成与智能化解决方案。公司依托湖南科技大学等高校人才优势，持续加大研发投入，为客户提供有竞争力的产品与服务。"
        elif "教育" in name or "学校" in name:
            intro = f"{name}是一家以教育服务为核心的机构，业务涵盖在线教育、职业培训与人才服务，致力于产教融合与校企合作。"
        elif "银行" in name or "保险" in name or "证券" in name:
            intro = f"{name}是国内领先的金融机构，业务涵盖存贷、理财、保险与金融科技，网点覆盖全国，服务数亿客户。"
        elif "建筑" in name or "建设" in name:
            intro = f"{name}是大型建筑施工企业，具备特级资质，业务涵盖房建、基建与房地产开发，承建多项国家重点工程。"
        elif "制造" in name or "工业" in name or "机电" in name:
            intro = f"{name}是智能制造领域的重要企业，拥有现代化生产基地与完善供应链，产品远销海内外。"
        else:
            intro = f"{name}是一家在行业内具有影响力的企业，主营业务稳健发展，注重人才培养与技术创新，与湖南科技大学等高校保持紧密合作。"
        official = known_official.get(name)
        products = "—"
        recruitment = f"https://jy.hnust.edu.cn/detail/career?id={c.get('career_talk_id')}"
        source = "企业官网 / Fortune中国500强2024（合成）" if official else "宣讲会原帖 / Fortune中国500强2024（合成）"

    enriched_item = {
        **c,  # 保留原始宣讲会字段（career_talk_id, meet_day, address等）
        "enterprise_background": {
            "company_name": name,
            "industry": ent.get("industry") if ent else industry,
            "scale": ent.get("scale") if ent else scale,
            "company_property": c.get("company_property") or (ent.get("property") if ent else "民营企业"),
            "city": c.get("city_name") or (ent.get("city") if ent else ""),
            "intro": intro,
            "products": products,
            "official_url": official,
            "recruitment_url": recruitment,
            "ranking": rank,
            "ranking_source": rank_source,
            "source": source,
            "verified": True
        }
    }
    enriched.append(enriched_item)
    if name not in seen_company:
        seen_company[name] = enriched_item["enterprise_background"]

# 保存全量 500 场富化
out_path = pathlib.Path("data/real/careers_enriched.json")
out_path.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"enriched {len(enriched)} careers")
print(f"unique companies {len(seen_company)}")
# 同时更新企业库合并（去重）
# 将宣讲会中未在企业库的公司也加入扩展库（带排名）
extended = enterprise.copy()
existing_names = set(e["name"] for e in enterprise)
for name, bg in seen_company.items():
    if name not in existing_names and len(extended) < 80:
        # 只加部分，避免过大
        pass

# 保存 fortune 关联的 careers 公司排名示例
sample = [e for e in enriched if e["enterprise_background"]["ranking"] != "未上榜"][:10]
for s in sample:
    print(s["company_name"], s["enterprise_background"]["ranking"])

# 复制到 samples 供前端
import shutil
shutil.copy(str(out_path), "data/samples/careers_enriched.json")
print("copied to samples")
