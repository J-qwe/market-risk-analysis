# 云服务器部署指南 - 获取固定网址

## 推荐方案排名

### 🥇 第一选择：Render.com（最简单）
- 免费额度
- 固定域名：`你的应用名.onrender.com`
- 5 分钟部署完成

### 🥈 第二选择：Railway.app
- 免费额度 $5/月
- 固定域名：`你的应用名.railway.app`
- UI 友好

### 🥉 第三选择：Fly.io
- 免费额度
- 固定域名：`你的应用名.fly.dev`
- 支持自定义域名

### 💪 国内方案：阿里云/腾讯云
- 固定 IP，可绑定域名
- 性能最好，延迟低
- 需要付费（¥40-100/月）

---

## 🚀 快速部署到 Render（5 分钟）

### 步骤 1：上传到 GitHub
```bash
# 初始化 git
git init
git add .
git commit -m "Initial commit"

# 上传到 GitHub
# 访问 https://github.com/new 创建仓库
git remote add origin https://github.com/你的用户名/market-risk-analysis.git
git push -u origin main
```

### 步骤 2：在 Render 创建应用
1. 访问：https://render.com
2. 点击 "New +"
3. 选择 "Web Service"
4. 连接你的 GitHub 仓库
5. 填写配置：
   - Name: `market-risk-analysis`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python src/frontend/streamlit_app.py --server.port=$PORT`
6. 点击 "Create Web Service"

**几分钟后，你会得到一个网址：**
```
https://market-risk-analysis.onrender.com
```

### 步骤 3：修改代码中的 API 地址
在 `src/frontend/streamlit_app.py` 中修改：
```python
# 原来的
API_BASE_URL = "http://localhost:5000/api"

# 改为
API_BASE_URL = "https://你的应用名.onrender.com/api"
```

---

## 📋 部署前需要修改的文件

### 1. requirements.txt（已有，检查是否完整）
```
Flask==2.3.3
flask-cors==4.0.0
streamlit==1.28.1
pandas==2.1.3
requests==2.31.0
# ... 其他依赖
```

### 2. runtime.txt（指定 Python 版本）
在项目根目录创建 `runtime.txt`：
```
python-3.11.0
```

### 3. .gitignore（已有）
确保包含：
```
__pycache__/
.streamlit/
*.pyc
.env
```

---

## 🔐 部署后的配置

### 修改 API 地址
部署后，Render 会给你一个公网 URL，比如：
```
https://market-risk-analysis.onrender.com
```

修改 `src/frontend/streamlit_app.py`：
```python
# 找到这行
API_BASE_URL = "http://localhost:5000/api"

# 改为
API_BASE_URL = "https://market-risk-analysis.onrender.com/api"
```

### 环境变量配置
在 Render 仪表板中设置环境变量：
```
FLASK_ENV=production
FLASK_DEBUG=false
```

---

## 💾 完整部署命令（如果使用本地服务器）

如果想在云服务器上手动部署：

```bash
# 1. SSH 连接到服务器
ssh root@your_server_ip

# 2. 克隆代码
git clone https://github.com/你的用户名/market-risk-analysis.git
cd market-risk-analysis

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动 API（后台运行）
nohup python src/api/app.py &

# 5. 启动 Streamlit（后台运行）
nohup streamlit run src/frontend/streamlit_app.py &

# 6. 配置 Nginx 反向代理（可选）
# ... 配置文件见下方
```

### Nginx 配置（可选，用于绑定域名）
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8502;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:5000;
    }
}
```

---

## 📊 方案对比

| 方案 | 费用 | 部署难度 | 域名 | 国内速度 |
|-----|------|---------|------|---------|
| Render | 免费/¥25/月 | ⭐ 超简单 | 固定二级域名 | 中等 |
| Railway | ¥0-30/月 | ⭐ 超简单 | 固定二级域名 | 中等 |
| Fly.io | 免费/¥29/月 | ⭐⭐ 简单 | 固定域名 | 中等 |
| 阿里云 | ¥40-100/月 | ⭐⭐⭐ 复杂 | 自定义域名 | 快速 ⚡ |
| 腾讯云 | ¥30-80/月 | ⭐⭐⭐ 复杂 | 自定义域名 | 快速 ⚡ |

---

## ⚡ 最快方案（推荐给你）

**使用 Render 部署，5 分钟获得固定网址：**

1. GitHub 上传代码（2分钟）
2. Render 连接 GitHub（1分钟）
3. 配置部署设置（1分钟）
4. 等待部署完成（1分钟）

**总耗时：5 分钟**

获得的网址：`https://market-risk-analysis.onrender.com`

---

## ❓ 需要帮助？

1. **帮你上传到 GitHub** ✅ 我可以做
2. **修改代码配置** ✅ 我可以做
3. **Render 部署配置** ✅ 我可以做

告诉我你选择哪个方案，我会帮你完成部署！
