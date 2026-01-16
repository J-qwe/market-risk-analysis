# 远程访问配置指南

## 🌍 让外网用户能访问你的应用

目前系统只能在局域网内访问。要让不在同一网络的人也能访问，有以下方案：

---

## 方案 1：ngrok 内网穿透（推荐 ⭐）

**最简单、最快速的方案。无需购买服务器。**

### 步骤 1：注册 ngrok 账户
```
访问: https://ngrok.com/sign-up
用邮箱注册免费账户
```

### 步骤 2：获取 Auth Token
```
登录后在这里复制 Token: https://dashboard.ngrok.com/auth/your-authtoken
看起来像: 2UnHpNnc5W9M5YYkWvk8eN8HEQk_...
```

### 步骤 3：运行远程访问脚本
```powershell
python remote_access.py
```

脚本会：
1. ✅ 检查依赖
2. ✅ 提示输入 ngrok Token
3. ✅ 自动生成公网 URL
4. ✅ 启动服务

### 步骤 4：分享链接
脚本会输出类似这样的公网 URL：
```
https://1a2b-192-168-1-100.ngrok-free.app
```

**分享这个链接给朋友，他们就可以从任何地方访问！**

---

## 方案 2：使用 CLI ngrok（无需 Python 集成）

### 步骤 1：下载 ngrok
```
访问: https://ngrok.com/download
下载 Windows 版本
```

### 步骤 2：解压到项目目录
```
.\ngrok.exe auth token YOUR_AUTH_TOKEN
```

### 步骤 3：启动 ngrok 代理
```powershell
# 新开一个 PowerShell 窗口
cd 项目目录
.\ngrok.exe http 8502
```

输出会显示：
```
Forwarding                    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:8502
```

---

## 方案 3：云服务器部署（长期方案）

如果需要永久可访问：
- 购买云服务器（阿里云、腾讯云等）
- 部署应用到云服务器
- 绑定域名

---

## 安全建议

⚠️ 启用远程访问后：

1. **添加密码保护**
   - 在 Streamlit 应用中添加登录页面

2. **设置访问限制**
   - 只分享链接给信任的人
   - 定期更换 ngrok URL

3. **HTTPS 加密**
   - ngrok 默认使用 HTTPS，传输已加密

4. **监控访问**
   - 查看 ngrok 仪表板的访问日志

---

## 常见问题

**Q: ngrok URL 在哪里显示？**
A: 在 terminal 窗口的输出中，会显示 `https://xxxx.ngrok-free.app`

**Q: URL 会变吗？**
A: 是的，每次重启都会变新的，除非升级到付费版

**Q: 需要一直开着电脑吗？**
A: 是的，直到停止脚本或关闭应用

**Q: 如果忘记输入 Token？**
A: 可以重新运行脚本，或手动设置：
```powershell
python -c "from pyngrok import ngrok; ngrok.set_auth_token('YOUR_TOKEN')"
```

---

## 快速启动

```powershell
# 方式 1：使用 Python 脚本
python remote_access.py

# 方式 2：使用 CLI
.\ngrok.exe http 8502
```

有问题？访问 ngrok 文档：https://ngrok.com/docs
