# -*- coding: utf-8 -*-
"""
SQLite数据库初始化脚本（无需MySQL）
"""
import sqlite3
import os

print("=" * 60)
print("社区医院门诊管理系统 - SQLite数据库初始化")
print("=" * 60)
print()

# 删除旧数据库
if os.path.exists('hospital.db'):
    print("删除旧数据库...")
    os.remove('hospital.db')

# 创建新数据库
print("正在创建SQLite数据库...")
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

print("正在创建数据表...")

# 1. 科室表
cursor.execute("""
CREATE TABLE IF NOT EXISTS department (
    dept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dept_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 2. 员工表
cursor.execute("""
CREATE TABLE IF NOT EXISTS employee (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_name TEXT NOT NULL,
    emp_type TEXT CHECK(emp_type IN ('医生', '护士', '行政人员')) NOT NULL,
    dept_id INTEGER,
    title TEXT,
    phone TEXT,
    work_status TEXT CHECK(work_status IN ('在职', '休假', '离职')) DEFAULT '在职',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
)
""")

# 3. 诊室表
cursor.execute("""
CREATE TABLE IF NOT EXISTS clinic_room (
    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_name TEXT NOT NULL,
    dept_id INTEGER NOT NULL,
    status TEXT CHECK(status IN ('开放', '关闭', '维护中')) DEFAULT '开放',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
)
""")

# 4. 患者表
cursor.execute("""
CREATE TABLE IF NOT EXISTS patient (
    patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('男', '女', '其他')),
    id_card TEXT UNIQUE,
    phone TEXT NOT NULL,
    address TEXT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# 5. 预约表
cursor.execute("""
CREATE TABLE IF NOT EXISTS appointment (
    appt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    patient_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    dept_id INTEGER NOT NULL,
    appt_date DATE NOT NULL,
    appt_time TIME NOT NULL,
    status TEXT CHECK(status IN ('待到院', '已到院', '已取消')) DEFAULT '待到院',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
)
""")

# 6. 就诊表
cursor.execute("""
CREATE TABLE IF NOT EXISTS visit (
    visit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    dept_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    doctor_id INTEGER,
    visit_date DATE NOT NULL,
    visit_time TIME NOT NULL,
    diagnosis TEXT,
    prescription TEXT,
    status TEXT CHECK(status IN ('等待就诊', '就诊中', '已完成', '已离院')) DEFAULT '等待就诊',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id),
    FOREIGN KEY (room_id) REFERENCES clinic_room(room_id),
    FOREIGN KEY (doctor_id) REFERENCES employee(emp_id)
)
""")

# 7. 费用表
cursor.execute("""
CREATE TABLE IF NOT EXISTS billing (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    visit_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    total_fee REAL NOT NULL,
    insurance_fee REAL DEFAULT 0.00,
    self_fee REAL NOT NULL,
    payment_method TEXT CHECK(payment_method IN ('现金', '微信', '支付宝', '银行卡', '医保卡')),
    payment_status TEXT CHECK(payment_status IN ('未支付', '已支付', '已退款')) DEFAULT '未支付',
    payment_time TIMESTAMP,
    operator_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES visit(visit_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (operator_id) REFERENCES employee(emp_id)
)
""")

# 8. 排班表
cursor.execute("""
CREATE TABLE IF NOT EXISTS doctor_schedule (
    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    room_id INTEGER NOT NULL,
    work_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    max_patients INTEGER DEFAULT 30,
    current_patients INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES employee(emp_id),
    FOREIGN KEY (room_id) REFERENCES clinic_room(room_id),
    UNIQUE (doctor_id, work_date, start_time)
)
""")

# 9. 系统用户表
cursor.execute("""
CREATE TABLE IF NOT EXISTS system_user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    user_role TEXT CHECK(user_role IN ('患者', '前台', '管理员')) NOT NULL,
    emp_id INTEGER,
    patient_id INTEGER,
    status TEXT CHECK(status IN ('启用', '禁用')) DEFAULT '启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employee(emp_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
)
""")

print("正在插入示例数据...")

# 插入科室
cursor.executemany("INSERT INTO department (dept_name, description) VALUES (?, ?)", [
    ('内科', '诊治内科常见疾病'),
    ('外科', '外科手术及治疗'),
    ('儿科', '儿童疾病诊治'),
    ('妇科', '妇科疾病诊治'),
    ('骨科', '骨科疾病及创伤治疗')
])

# 插入员工
cursor.executemany("""
    INSERT INTO employee (emp_name, emp_type, dept_id, title, phone, work_status) 
    VALUES (?, ?, ?, ?, ?, ?)
""", [
    ('张文博', '医生', 1, '主任医师', '13800138001', '在职'),
    ('李明华', '医生', 1, '副主任医师', '13800138002', '在职'),
    ('王建国', '医生', 2, '主治医师', '13800138003', '在职'),
    ('赵雅琴', '护士', 1, '护师', '13800138004', '在职'),
    ('刘芳', '行政人员', None, '收费员', '13800138005', '在职'),
    ('陈志强', '行政人员', None, '医务科主任', '13800138006', '在职')
])

# 插入诊室
cursor.executemany("INSERT INTO clinic_room (room_name, dept_id, status) VALUES (?, ?, ?)", [
    ('内科1诊室', 1, '开放'),
    ('内科2诊室', 1, '开放'),
    ('外科1诊室', 2, '开放'),
    ('儿科1诊室', 3, '开放'),
    ('妇科1诊室', 4, '开放')
])

# 插入排班
cursor.executemany("""
    INSERT INTO doctor_schedule (doctor_id, room_id, work_date, start_time, end_time, max_patients)
    VALUES (?, ?, date('now'), ?, ?, ?)
""", [
    (1, 1, '08:00:00', '12:00:00', 30),
    (1, 1, '14:00:00', '17:00:00', 30),
    (2, 2, '08:00:00', '12:00:00', 30),
    (3, 3, '08:00:00', '17:00:00', 40)
])

# 插入系统用户
cursor.executemany("""
    INSERT INTO system_user (username, password, user_role, emp_id, patient_id)
    VALUES (?, ?, ?, ?, ?)
""", [
    ('admin', '123456', '管理员', 6, None),
    ('receptionist', '123456', '前台', 5, None),
    ('patient_demo', '123456', '患者', None, None)
])

conn.commit()

print()
print("=" * 60)
print("✓ SQLite数据库创建成功！")
print("=" * 60)
print()
print("数据库文件: hospital.db")
print("已创建:")
print("  - 9张数据表")
print("  - 示例数据（科室、员工、诊室等）")
print()
print("测试账号（密码都是 123456）:")
print("  - 管理员: admin")
print("  - 前台: receptionist")
print("  - 患者: patient_demo")
print()
print("接下来:")
print("  1. 运行: python app.py")
print("  2. 访问: http://localhost:5000")
print()

cursor.close()
conn.close()

print("按任意键退出...")
input()
