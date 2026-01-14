# -*- coding: utf-8 -*-
"""
数据库初始化脚本
自动创建数据库和表
"""

import pymysql
import getpass

def init_database():
    print("=" * 50)
    print("社区医院门诊管理系统 - 数据库初始化")
    print("=" * 50)
    print()
    
    # 获取MySQL密码
    mysql_password = getpass.getpass("请输入MySQL的root密码: ")
    
    try:
        # 连接MySQL（不指定数据库）
        print("\n正在连接MySQL...")
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password=mysql_password,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # 读取SQL文件
        print("正在读取SQL脚本...")
        with open('database/schema.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行SQL脚本（分割成单条语句）
        print("正在创建数据库和表...")
        statements = sql_script.split(';')
        
        for i, statement in enumerate(statements):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    if i % 5 == 0:
                        print(f"  进度: {i}/{len(statements)} 条语句已执行")
                except Exception as e:
                    # 忽略一些无关紧要的错误
                    if "already exists" not in str(e):
                        print(f"  警告: {str(e)[:100]}")
        
        conn.commit()
        
        print("\n✓ 数据库创建成功！")
        print("\n已创建的内容：")
        print("  - 数据库: hospital_management")
        print("  - 10张数据表")
        print("  - 示例数据（科室、员工、诊室等）")
        print("  - 测试账号：")
        print("    * 管理员: admin / 123456")
        print("    * 前台: receptionist / 123456")
        print("    * 患者: patient_demo / 123456")
        
        print("\n接下来的步骤：")
        print("1. 修改 app.py 文件第20行的数据库密码")
        print(f"   'password': '{mysql_password}',")
        print("2. 运行: python app.py")
        print("3. 访问: http://localhost:5000")
        
        cursor.close()
        conn.close()
        
        # 自动修改app.py中的密码
        update_app_password(mysql_password)
        
        return True
        
    except Exception as e:
        print(f"\n✗ 数据库创建失败: {str(e)}")
        print("\n请检查：")
        print("1. MySQL密码是否正确")
        print("2. MySQL服务是否正在运行")
        print("3. 是否有创建数据库的权限")
        return False

def update_app_password(password):
    """自动更新app.py中的数据库密码"""
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找并替换密码
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "'password':" in line and "'password': ''" in line:
                lines[i] = f"    'password': '{password}',  # MySQL密码"
                print(f"\n✓ 已自动更新 app.py 中的数据库密码")
                break
        
        # 写回文件
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
            
    except Exception as e:
        print(f"\n提示: 请手动修改 app.py 中的密码: {str(e)}")

if __name__ == '__main__':
    init_database()
    print("\n按任意键退出...")
    input()
