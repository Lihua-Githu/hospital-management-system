@echo off
chcp 65001 >nul
echo ========================================
echo 社区医院门诊管理系统 - 启动服务
echo ========================================
echo.

echo 正在启动Flask服务器...
echo 启动后请访问: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo.

python app.py

pause
