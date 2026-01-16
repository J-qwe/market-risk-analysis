#!/usr/bin/env python
"""
简易远程访问启动脚本 - 使用 ngrok 进行内网穿透
只需运行此脚本，自动生成公网访问链接
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path

def print_header():
    print("\n" + "=" * 70)
    print("  市场舆情风险挖掘系统 - 远程访问配置助手")
    print("=" * 70 + "\n")

def check_ngrok():
    """检查 ngrok 安装"""
    print("📋 检查依赖环境...\n")
    
    try:
        import pyngrok
        print("✅ pyngrok 已安装")
        return True
    except ImportError:
        print("❌ pyngrok 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok", "-q"])
        print("✅ pyngrok 安装完成\n")
        return True

def get_ngrok_token():
    """获取 ngrok token"""
    print("\n" + "=" * 70)
    print("🔑 ngrok 配置")
    print("=" * 70)
    print("""
ngrok 是一个内网穿透工具，可以让外网访问你的本地应用。

👉 快速开始步骤:

1. 访问: https://ngrok.com/sign-up
2. 使用邮箱注册免费账户
3. 登录后复制你的 Auth Token
4. 在下方粘贴 Token

示例 Token 看起来像: 2UnHpNnc5W9M5YYkWvk8eN8HEQk_...
""")
    
    while True:
        token = input("📝 请输入你的 ngrok Auth Token (或按 Enter 跳过): ").strip()
        
        if not token:
            print("\n⚠️  跳过 ngrok 配置")
            print("💡 您可以在稍后手动配置，访问上述网址获取 Token")
            return None
            
        if len(token) > 10:  # 基本验证
            return token
        else:
            print("❌ Token 格式不正确，请重试")

def setup_ngrok(token):
    """设置 ngrok"""
    try:
        import pyngrok
        pyngrok.conf.get_ngrok_path()
        
        if token:
            # 设置 auth token
            from pyngrok import ngrok as ngrok_module
            ngrok_module.set_auth_token(token)
            print("✅ ngrok Token 已设置")
            return True
        return False
    except Exception as e:
        print(f"⚠️  ngrok 设置出错: {e}")
        return False

def start_services():
    """启动服务"""
    print("\n" + "=" * 70)
    print("🚀 启动远程访问模式")
    print("=" * 70 + "\n")
    
    try:
        from pyngrok import ngrok
        
        print("⏳ 启动前端应用...")
        # Streamlit 会在 8502 端口启动
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "src/frontend/streamlit_app.py"],
            cwd="."
        )
        
        time.sleep(3)  # 等待 Streamlit 启动
        
        print("🌐 创建 ngrok 隧道...")
        public_url = ngrok.connect(8502, "http")
        
        print("\n" + "=" * 70)
        print("✅ 远程访问已启用!")
        print("=" * 70)
        print(f"\n📍 公网访问链接:\n   {public_url}\n")
        print("💡 分享此链接给其他人，他们就可以从任何地方访问\n")
        print("🔒 安全提示:")
        print("   - 这是临时链接，重启后会改变")
        print("   - 建议添加访问密码\n")
        print("=" * 70)
        print("⏳ 服务运行中... (按 Ctrl+C 停止)\n")
        
        # 保持运行
        frontend_process.wait()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

def main():
    os.chdir(Path(__file__).parent)
    
    print_header()
    
    # 检查依赖
    if not check_ngrok():
        sys.exit(1)
    
    # 获取 token
    token = get_ngrok_token()
    
    # 设置 ngrok
    if token:
        setup_ngrok(token)
        start_services()
    else:
        print("\n💡 您需要 ngrok Token 来启用远程访问")
        print("   1. 访问: https://ngrok.com/sign-up")
        print("   2. 获取 Auth Token")
        print("   3. 重新运行此脚本\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 已停止服务")
        sys.exit(0)
