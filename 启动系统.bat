@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   医院门诊管理系统 - 快速启动
echo ========================================
echo.
echo [1/3] 检查环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ 未找到Python，请先安装Python
    pause
    exit
)
echo ✓ Python环境正常

echo.
echo [2/3] 检查数据库...
if not exist hospital.db (
    echo ✗ 数据库不存在，正在初始化...
    python init_sqlite.py
    if errorlevel 1 (
        echo ✗ 数据库初始化失败
        pause
        exit
    )
)
echo ✓ 数据库就绪

echo.
echo [3/3] 启动服务器...
echo.
echo ========================================
echo   系统已启动！
echo   访问地址: http://localhost:5000
echo   按 Ctrl+C 可停止服务器
echo ========================================
echo.
python app.py
