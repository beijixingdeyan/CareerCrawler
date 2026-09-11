@echo off
echo [CareerCrawler] 启动后端 + 前端构建检查
python scripts/seed.py
if not exist frontend\dist (
  echo 前端未构建，正在构建...
  cd frontend && call npm install && call npm run build && cd ..
)
echo 启动后端 http://127.0.0.1:8000
python -m uvicorn backend.app.main:app --reload --port 8000
