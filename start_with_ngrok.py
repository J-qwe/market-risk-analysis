"""
使用 ngrok 实现远程访问的启动脚本
可以让不在同一局域网的人也能访问系统
"""

import subprocess
import time
import webbrowser
from pyngrok import ngrok

def main():
    print("=" * 60)
    print("  市场舆情风险挖掘系统 - 远程访问模式")
    print("=" * 60)
    print()
    
    # 创建 ngrok 隧道指向 Streamlit 前端
    print("🚀 启动内网穿透...")
    print()
    
    try:
        # 获取 Streamlit 前端公网 URL
        public_url = ngrok.connect(8502, "http")
        print(f"✅ 远程访问 URL 已生成！")
        print()
        print(f"📍 外网访问地址: {public_url}")
        print()
        print("=" * 60)
        print("🌐 分享给朋友的访问链接:")
        print(f"   {public_url}")
        print("=" * 60)
        print()
        print("⏳ 服务正在运行中...")
        print("按 Ctrl+C 停止")
        print()
        
        # 保持运行
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        print()
        print("💡 解决方案:")
        print("1. 首先访问 https://ngrok.com/sign-up 注册免费账户")
        print("2. 复制 Auth Token")
        print("3. 运行: ngrok config add-authtoken YOUR_AUTH_TOKEN")
        print("4. 重新运行此脚本")

if __name__ == "__main__":
    main()
