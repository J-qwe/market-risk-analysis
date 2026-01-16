@echo off
chcp 65001 >nul
echo ========================================
echo  市场舆情风险挖掘系统
echo ========================================
echo.

echo 📦 检查项目结构...
if not exist "src\api\app.py" (
    echo ❌ 错误：找不到 API 文件
    pause
    exit /b 1
)

if not exist "src\frontend\streamlit_app.py" (
    echo ❌ 错误：找不到前端文件
    pause
    exit /b 1
)

echo ✅ 项目结构检查通过

echo.
echo 🚀 启动API服务...
start "API服务" cmd /k "cd /d src\api && python app.py"

echo ⏳ 等待API服务启动...
timeout /t 3 /nobreak >nul

echo.
echo 🌐 启动前端界面...
start "前端界面" cmd /k "cd /d src\frontend && streamlit run streamlit_app.py"

echo.
echo ========================================
echo  ✅ 启动完成！
echo ========================================
echo.
echo 📍 访问地址：
echo 1. 前端界面: http://localhost:8501
echo 2. API服务: http://localhost:5000
echo.
echo 📋 使用说明：
echo 1. 在浏览器中打开前端界面
echo 2. 在侧边栏选择股票和设置
echo 3. 点击"开始分析"按钮
echo 4. 查看风险文章和简报
echo.
pause