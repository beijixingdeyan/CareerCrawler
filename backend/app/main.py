from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pathlib

from .database import init_db
from .routers import jobs, companies, analysis, recommend, careers, jobfairs

app = FastAPI(
    title="CareerCrawler API",
    version="1.0.0",
    description="校园就业信息智能采集与分析平台 - 湖南科技大学专版 | CareerCrawler",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(jobs.router)
app.include_router(companies.router)
app.include_router(analysis.router)
app.include_router(recommend.router)
app.include_router(careers.router)
app.include_router(jobfairs.router)

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CareerCrawler", "version": "1.0.0", "school": "HNUST"}

@app.get("/api/meta")
def meta():
    return {
        "school": "湖南科技大学",
        "college": "计算机科学与工程学院",
        "fair": {"id": "30003", "name": "2027届计算机类毕业生专场招聘会", "time": "2026-09-22 14:30", "location": "敏行楼C212", "graduates": {"本科813": ["软件139","信安129","物联网116","大数据131","计科298"], "硕士106": ["软件52","计科27","计技27"], "博士13": ["软件13"]}},
        "sources": ["jy.hnust.edu.cn/module/careers", "jy.hnust.edu.cn/module/jobfairs", "jy.hnust.edu.cn/module/jobs"],
        "token": "yxqqnn0000000006 (public)"
    }

# Serve frontend static if built — SPA fallback (careers / jobfairs 分栏)
FRONT_DIST = pathlib.Path(__file__).resolve().parents[2] / "frontend" / "dist"
if FRONT_DIST.exists():
    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        # 1. 静态资源直接返回
        file = FRONT_DIST / full_path
        if full_path and file.exists() and file.is_file():
            return FileResponse(str(file))
        # 2. API 已在上方匹配，剩余前端路由全部回 index.html（支持 /careers /jobfairs）
        index = FRONT_DIST / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"detail": "frontend not built"}

    # 静态资源兜底（assets 等）
    app.mount("/", StaticFiles(directory=str(FRONT_DIST), html=True), name="frontend")
