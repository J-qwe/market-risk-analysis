#!/bin/bash

# 启动脚本 - 在 Render 上同时运行 API 和前端

# 启动 API 服务（后台）
echo "🚀 启动 API 服务..."
python src/api/app.py &
API_PID=$!

# 等待 API 启动
sleep 2

# 启动 Streamlit 前端
echo "🌐 启动 Streamlit 前端..."
streamlit run src/frontend/streamlit_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --logger.level=info \
    --client.toolbarMode=minimal \
    --browser.gatherUsageStats=false

# 后台进程清理
wait $API_PID
