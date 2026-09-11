#!/bin/bash
set -e
echo "[CareerCrawler] seed DB..."
python scripts/seed.py
if [ ! -d "frontend/dist" ]; then
  echo "前端未构建，正在构建..."
  cd frontend && npm install && npm run build && cd ..
fi
echo "启动后端 http://127.0.0.1:8000"
python -m uvicorn backend.app.main:app --reload --port 8000
