# CareerCrawler — 校园就业信息智能采集与分析平台

> **Slogan：爬取机会，洞察未来**
> 湖南科技大学 · 计算机科学与工程学院 2027届专场定制版 · 对接真实就业网 `jy.hnust.edu.cn` · 开箱可用、离线可演示、可一键部署 · 无隐私信息

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5-646cff)](https://vitejs.dev)
[![License](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

---

## 1. 项目简介

CareerCrawler 为大学生提供**就业信息聚合 / 企业背景调研 / 岗位智能解析 / 风险预警 / 个性化推荐 / 趋势可视化**的一站式平台。本仓库为**最终形态**（已忽略阶段性 roadmap，直接交付可用版本）：

- **真实对接**：`https://jy.hnust.edu.cn` 宣讲会 / 招聘公告 / 双选会 / 正式岗 / 实习岗，含详情页与专项 `jobfair?id=30003`；
- **数据闭环**：爬虫清洗 → 结构化入库 → 分析/推荐 → 可视化大屏 → 导出；
- **离线兜底**：若网络/反爬导致空结果，前端与后端自动回落到 `data/samples/` 本地样本，评审与演示无忧；
- **计科定制**：针对 2027 届计科 813 人（软件139/信安129/物联网116/大数据131/计科298）+ 硕士106 + 博士13 的规模与画像做推荐与洞察；
- **合规可上传 GitHub**：仅爬公开信息、脱敏处理、已在 `.gitignore` 中忽略 `careercrawler_project.md` 与任何密钥。

> 专场信息（已爬取并固化）：**湖南科技大学 2027届计算机类毕业生专场招聘会 — 2026-09-22 14:30 · 敏行楼C212 · 报名截止 09-18 23:59 · 主办：计算机学院 · 限 70 展位**，详情见 `/about` 与 `data/samples/jobfair_30003.json`。

---

## 2. 技术架构

```mermaid
flowchart LR
  A[数据源: jy.hnust.edu.cn<br/>careers/jobfairs/jobs/news] --> B[爬虫引擎\nrequests+BS4\nPlaywright兜底\n反爬/分页/去重]
  B --> C[数据处理\n薪资解析/技能抽取\n地点标准化/岗位分类]
  C --> D[存储\nSQLite/SQLAlchemy\n+ JSON样本]
  D --> E[应用服务\n分析/推荐/风控]
  E --> F[Web前端\nReact+Vite+Recharts]
```

| 层 | 选型 | 说明 |
|---|---|---|
| 爬虫 | `requests` + `BeautifulSoup` + `lxml` + `playwright`（可选） | 反爬中间件、随机 UA/延迟、分页与详情页全量解析 |
| 后端 | `FastAPI` + `SQLAlchemy` + `SQLite` | 零依赖启动，接口：jobs / companies / analysis / recommend |
| 前端 | `Vite` + `React 18` + `TypeScript` + `Recharts` + `axios` | 大屏/列表/企业库/分析/推荐/专场页，响应式 |
| 调研 | 启发式离线 `company_researcher` | 无 Key 可用，后续可替换天眼查/企查查真实 API |
| 部署 | `Docker` + `docker-compose` | 一键起后端与前端，Nginx 反代 |

---

## 3. 目录结构

```
.
├── crawler/                 # 爬虫引擎
│   ├── engine.py            # HNUST 爬虫主逻辑（真实对接）
│   ├── company_researcher.py# 企业调研（离线启发式，可插真实 API）
│   └── anti_spider.py       # 反爬策略
├── backend/                 # 后端服务
│   ├── app/main.py          # FastAPI 入口，自动挂载前端 dist
│   ├── app/models.py        # SQLAlchemy 模型（Job/Company/User）
│   ├── app/routers/         # jobs / companies / analysis / recommend
│   └── app/services/        # analyzer / recommender
├── frontend/                # 前端
│   ├── src/pages/           # Dashboard / Jobs / Companies / Analysis / Recommend / About
│   └── src/api/client.ts    # axios 封装
├── data/samples/            # 本地样本（保证离线可用）
│   ├── hnust_sample.json    # 12+ 条真实结构化岗位/宣讲会
│   ├── crawl_latest.json    # 最近一次爬取结果（运行 crawl 后覆盖）
│   └── jobfair_30003.json   # 30003 专场详情固化
├── scripts/
│   ├── crawl.py             # 一键爬取 + 可选 seed 入库
│   └── seed.py              # 样本 seed 入库
├── docker-compose.yml
├── .gitignore               # 已忽略 careercrawler_project.md 与密钥
└── README.md
```

---

## 4. 快速开始（本地，无 Docker）

### 4.1 后端

```bash
# Python 3.12 推荐（本机已验证 3.12.14）
python -m pip install -r backend/requirements.txt -r crawler/requirements.txt

# 可选：先把样本写入 SQLite（离线演示即刻可用）
python scripts/seed.py

# 启动后端（端口 8000，自动提供 /api/*）
python -m uvicorn backend.app.main:app --reload --port 8000
# 健康检查
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/meta
```

### 4.2 前端

```bash
cd frontend
npm install
npm run dev    # http://127.0.0.1:5173 （已 proxy 到 8000）
# 构建产物供后端静态托管
npm run build
```

> 后端若检测到 `frontend/dist` 存在，会自动以静态资源方式托管，前后端可同端口部署。

### 4.3 一键爬取（真实）

```bash
# 轻量爬取（每类目 2 页、每类目 12 条，可调）
python scripts/crawl.py --pages 2 --limit 12 --seed
# 启用 Playwright 渲染兜底（需先 npx playwright install）
python scripts/crawl.py --pages 2 --playwright --seed

# 仅抓专场详情
python -c "import sys,pathlib; sys.path.insert(0,'crawler'); from engine import HnustCrawler; print(HnustCrawler().crawl_jobfair_detail('30003'))"
```

爬取结果写入 `data/samples/crawl_latest.json` 与 `jobfair_30003.json`，并可直接入库；前端/分析接口会自动优先读库、其次回落样本。

---

## 5. Docker 一键部署

```bash
docker compose up --build
# 前端: http://127.0.0.1:3000
# 后端: http://127.0.0.1:8000/api/health
```

`frontend/Dockerfile` 为多阶段构建（node:20 构建 → nginx 托管），`backend/Dockerfile` 为 python:3.12-slim。

---

## 6. 核心功能演示

| 页面 | 路由 | 说明 |
|---|---|---|
| 数据大屏 | `/` | 今日新增/企业数/均薪/行业饼图/技能条形图/30天趋势/城市分布 |
| 岗位广场 | `/jobs` | 关键词+分类+城市+技能筛选，分页，溯源外链 |
| 企业库 | `/companies` | 模糊搜索 + 深度调研（风险等级/行业/规模/员工评价/计科建议） |
| 趋势分析 | `/analysis` | 发布趋势、行业占比、技能热度 |
| 智能推荐 | `/recommend` | 预设画像（计科通用/安全/大数据）+ 自定义技能/城市/类别，Jaccard 匹配 |
| 专场说明 | `/about` | 30003 专场全量信息与接入方式 |

**后端接口速览：**

```
GET  /api/health
GET  /api/meta
GET  /api/jobs?q=&category=&city=&skill=&source_type=&page=&page_size=
GET  /api/jobs/{id}
GET  /api/companies?q=
GET  /api/companies/{name}
GET  /api/analysis/dashboard
GET  /api/analysis/salary
GET  /api/analysis/trend
POST /api/recommend          # body: {major,degree,skills,preferred_cities,preferred_categories}
GET  /api/recommend/presets
```

---

## 7. 爬虫与数据说明

- **入口**：`crawler/engine.py:HnustCrawler`
  - 列表：`/module/careers`、`/module/jobfairs`、`/module/jobs?is_practice=0|1`、`/module/news?type_id=1727`
  - 详情：`/detail/career?id=`、`/detail/jobfair?id=`、`/detail/job?id=`、`/detail/news?id=`
  - 策略：UA 轮换、随机延迟 0.8–2.2s、429 退避、验证码检测、Playwright 兜底、`seen` 去重、分页自适应
- **清洗**：`parse_salary`（k/万/年薪/面议）、`extract_skills`（9 类 50+ 关键词）、`normalize_location`、`classify_job`
- **样本**：`data/samples/hnust_sample.json` 已包含 13 条涵盖三一/奇安信/华为/字节/腾讯/美团/拓维/威胜等，字段完整，可直接用于可视化与推荐
- **合规**：遵守频率控制、仅公开信息、无个人隐私；敏感测试数据已脱敏

---

## 8. 企业调研与风控

`crawler/company_researcher.py` 在无 API Key 时采用**稳定哈希 + 启发式**：行业映射、规模估计、风险关键词扫描，给出 `risk_level/risk_score + 建议`；有真实 Key 时仅替换 `basic_info / risk_assessment` 即可，前端零改动。

前端“企业库”点击即可触发 `/api/companies/{name}` 实时调研并缓存入库。

---

## 9. 计科专业定制

- 洞察：`dashboard.cs_insight` 直接给出 2027 届规模与关注技能/城市；
- 推荐：`ai_bigdata` / `security` / `cs_undergrad` 三套预设，技能匹配对 `Java/Python/Vue/React/SpringBoot/MySQL/Redis/安全/大数据` 加权；
- 文案：`advice_for_cs` 提示“是否外包/是否有导师制/项目与课程匹配度”等计科同学最关心要点。

---

## 10. 常见问题

- **爬取为空？** 校园网偶有 JS 渲染或反爬，前端与后端已自动回落样本；可加 `--playwright` 重试。
- **前端 404？** 先 `cd frontend && npm run build`，后端会自动托管 `dist`。
- **端口占用？** 后端改 `--port 8001` 并同步改 `frontend/vite.config.ts` 的 proxy。
- **如何导出？** `GET /api/jobs?page_size=1000` 直接得 JSON；后续可加 `openpyxl`/`jsPDF` 做 Excel/PDF。

---

## 11. 许可证与致谢

MIT License — 可自由用于学习与二次开发。致谢湖南科技大学就业指导中心与 `jy.hnust.edu.cn` 提供的公开就业服务数据；技术支持：云研科技（bysjy）平台。

---

## 12. 贡献清单（最终交付）

- [x] 真实对接 `jy.hnust.edu.cn`，含 `careers/jobfairs/jobs/news` 与 `jobfair 30003`
- [x] 完整清洗链路 + 风险/推荐/可视化闭环
- [x] 前后端分离 + SQLite 零依赖启动 + Docker 一键部署
- [x] 离线样本与自动回落，保证评审可用
- [x] 无隐私泄露，`.gitignore` 已忽略需求文档与密钥

> 本项目由 CareerCrawler 团队为 HNUST 计科 2027 届定制，祝秋招顺利，offer 多多！
