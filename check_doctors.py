import sqlite3

conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

# 查询医生
cursor.execute("SELECT emp_id, emp_name, title, dept_id, emp_type FROM employee WHERE emp_type='医生' LIMIT 10")
rows = cursor.fetchall()

print(f'医生数量: {len(rows)}')
if len(rows) > 0:
    for row in rows:
        print(f"ID: {row[0]}, 姓名: {row[1]}, 职称: {row[2]}, 科室ID: {row[3]}, 类型: {row[4]}")
else:
    print("没有找到医生数据")
    
# 查询所有员工类型
cursor.execute("SELECT DISTINCT emp_type FROM employee")
types = cursor.fetchall()
print(f"\n员工类型: {[t[0] for t in types]}")

conn.close()
