@echo off
chcp 65001 >nul
echo ========================================
echo 社区医院门诊管理系统 - 数据库初始化
echo ========================================
echo.

set MYSQL_PATH="C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"

echo 请输入MySQL的root密码：
set /p MYSQL_PASSWORD=

echo.
echo 正在创建数据库...
%MYSQL_PATH% -u root -p%MYSQL_PASSWORD% < database\schema.sql

if %errorlevel% equ 0 (
    echo.
    echo ✓ 数据库创建成功！
    echo.
    echo 接下来的步骤：
    echo 1. 修改 app.py 文件中的数据库密码
    echo 2. 运行: python app.py
    echo 3. 访问: http://localhost:5000
    echo.
) else (
    echo.
    echo ✗ 数据库创建失败，请检查：
    echo 1. MySQL密码是否正确
    echo 2. MySQL服务是否正在运行
    echo.
)

pause
