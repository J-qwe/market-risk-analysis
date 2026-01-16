#!/bin/bash

# 启动脚本 - 在 Render 上运行 Streamlit 前端
# 前端使用内置的本地爬虫，不依赖 API 服务

echo "🌐 启动 Streamlit 前端..."
streamlit run src/frontend/streamlit_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --logger.level=info \
    --client.toolbarMode=minimal \
    --browser.gatherUsageStats=false
