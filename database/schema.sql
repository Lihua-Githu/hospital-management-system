-- 社区医院门诊管理系统数据库设计
-- 创建数据库
CREATE DATABASE IF NOT EXISTS hospital_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hospital_management;

-- 1. 科室表
CREATE TABLE department (
    dept_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '科室ID',
    dept_name VARCHAR(50) NOT NULL UNIQUE COMMENT '科室名称',
    description TEXT COMMENT '科室描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT='科室信息表';

-- 2. 员工表（医生、护士、行政人员）
CREATE TABLE employee (
    emp_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '工号',
    emp_name VARCHAR(50) NOT NULL COMMENT '姓名',
    emp_type ENUM('医生', '护士', '行政人员') NOT NULL COMMENT '员工类型',
    dept_id INT COMMENT '所属科室',
    title VARCHAR(50) COMMENT '职称',
    phone VARCHAR(20) COMMENT '联系电话',
    work_status ENUM('在职', '休假', '离职') DEFAULT '在职' COMMENT '工作状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) COMMENT='员工信息表';

-- 3. 诊室表
CREATE TABLE clinic_room (
    room_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '诊室编号',
    room_name VARCHAR(50) NOT NULL COMMENT '诊室名称',
    dept_id INT NOT NULL COMMENT '所属科室',
    status ENUM('开放', '关闭', '维护中') DEFAULT '开放' COMMENT '诊室状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (dept_id) REFERENCES department(dept_id)
) COMMENT='诊室信息表';

-- 4. 医生排班表
CREATE TABLE doctor_schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '排班ID',
    doctor_id INT NOT NULL COMMENT '医生工号',
    room_id INT NOT NULL COMMENT '诊室编号',
    work_date DATE NOT NULL COMMENT '排班日期',
    start_time TIME NOT NULL COMMENT '开始时间',
    end_time TIME NOT NULL COMMENT '结束时间',
    max_patients INT DEFAULT 30 COMMENT '最大接诊人数',
    current_patients INT DEFAULT 0 COMMENT '当前预约人数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (doctor_id) REFERENCES employee(emp_id),
    FOREIGN KEY (room_id) REFERENCES clinic_room(room_id),
    UNIQUE KEY unique_schedule (doctor_id, work_date, start_time)
) COMMENT='医生排班表';

-- 5. 患者信息表
CREATE TABLE patient (
    patient_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '患者ID',
    patient_name VARCHAR(50) NOT NULL COMMENT '姓名',
    gender ENUM('男', '女', '其他') COMMENT '性别',
    id_card VARCHAR(18) UNIQUE COMMENT '身份证号',
    phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    address TEXT COMMENT '住址',
    medical_history TEXT COMMENT '病史',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_phone (phone),
    INDEX idx_id_card (id_card)
) COMMENT='患者信息表';

-- 6. 预约信息表
CREATE TABLE appointment (
    appt_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '预约ID',
    patient_id INT COMMENT '患者ID（可为空，支持新患者预约）',
    patient_name VARCHAR(50) NOT NULL COMMENT '患者姓名',
    phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    dept_id INT NOT NULL COMMENT '就诊科室',
    appt_date DATE NOT NULL COMMENT '预约日期',
    appt_time TIME NOT NULL COMMENT '预计到达时间',
    status ENUM('待到院', '已到院', '已取消') DEFAULT '待到院' COMMENT '预约状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '预约时间',
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id),
    INDEX idx_appt_date (appt_date),
    INDEX idx_phone (phone)
) COMMENT='预约信息表';

-- 7. 就诊信息表
CREATE TABLE visit (
    visit_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '就诊ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    dept_id INT NOT NULL COMMENT '就诊科室',
    room_id INT NOT NULL COMMENT '诊室编号',
    doctor_id INT COMMENT '接诊医生',
    visit_date DATE NOT NULL COMMENT '就诊日期',
    visit_time TIME NOT NULL COMMENT '就诊时间',
    diagnosis TEXT COMMENT '诊断结果',
    prescription TEXT COMMENT '处方',
    status ENUM('等待就诊', '就诊中', '已完成', '已离院') DEFAULT '等待就诊' COMMENT '就诊状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '登记时间',
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id),
    FOREIGN KEY (room_id) REFERENCES clinic_room(room_id),
    FOREIGN KEY (doctor_id) REFERENCES employee(emp_id),
    INDEX idx_visit_date (visit_date),
    INDEX idx_status (status)
) COMMENT='就诊信息表';

-- 8. 费用结算表
CREATE TABLE billing (
    bill_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '账单ID',
    visit_id INT NOT NULL COMMENT '就诊ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    total_fee DECIMAL(10, 2) NOT NULL COMMENT '总费用',
    insurance_fee DECIMAL(10, 2) DEFAULT 0.00 COMMENT '医保支付',
    self_fee DECIMAL(10, 2) NOT NULL COMMENT '自费金额',
    payment_method ENUM('现金', '微信', '支付宝', '银行卡', '医保卡') COMMENT '支付方式',
    payment_status ENUM('未支付', '已支付', '已退款') DEFAULT '未支付' COMMENT '支付状态',
    payment_time TIMESTAMP NULL COMMENT '支付时间',
    operator_id INT COMMENT '收费员工号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (visit_id) REFERENCES visit(visit_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
    FOREIGN KEY (operator_id) REFERENCES employee(emp_id),
    INDEX idx_payment_time (payment_time)
) COMMENT='费用结算表';

-- 9. 收入统计表（冗余表，用于快速统计）
CREATE TABLE revenue_summary (
    summary_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '统计ID',
    stat_date DATE NOT NULL COMMENT '统计日期',
    dept_id INT COMMENT '科室ID',
    doctor_id INT COMMENT '医生ID',
    total_visits INT DEFAULT 0 COMMENT '就诊人次',
    total_revenue DECIMAL(10, 2) DEFAULT 0.00 COMMENT '总收入',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY unique_stat (stat_date, dept_id, doctor_id),
    FOREIGN KEY (dept_id) REFERENCES department(dept_id),
    FOREIGN KEY (doctor_id) REFERENCES employee(emp_id)
) COMMENT='收入统计表';

-- 10. 系统用户表（登录管理）
CREATE TABLE system_user (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码（加密存储）',
    user_role ENUM('患者', '前台', '管理员') NOT NULL COMMENT '用户角色',
    emp_id INT COMMENT '关联员工ID',
    patient_id INT COMMENT '关联患者ID',
    status ENUM('启用', '禁用') DEFAULT '启用' COMMENT '账户状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (emp_id) REFERENCES employee(emp_id),
    FOREIGN KEY (patient_id) REFERENCES patient(patient_id)
) COMMENT='系统用户表';

-- 插入示例数据

-- 插入科室
INSERT INTO department (dept_name, description) VALUES
('内科', '诊治内科常见疾病'),
('外科', '外科手术及治疗'),
('儿科', '儿童疾病诊治'),
('妇科', '妇科疾病诊治'),
('骨科', '骨科疾病及创伤治疗');

-- 插入员工
INSERT INTO employee (emp_name, emp_type, dept_id, title, phone, work_status) VALUES
('张医生', '医生', 1, '主任医师', '13800138001', '在职'),
('李医生', '医生', 1, '副主任医师', '13800138002', '在职'),
('王医生', '医生', 2, '主治医师', '13800138003', '在职'),
('赵护士', '护士', 1, '护师', '13800138004', '在职'),
('刘前台', '行政人员', NULL, '收费员', '13800138005', '在职'),
('陈主任', '行政人员', NULL, '医务科主任', '13800138006', '在职');

-- 插入诊室
INSERT INTO clinic_room (room_name, dept_id, status) VALUES
('内科1诊室', 1, '开放'),
('内科2诊室', 1, '开放'),
('外科1诊室', 2, '开放'),
('儿科1诊室', 3, '开放'),
('妇科1诊室', 4, '开放');

-- 插入医生排班
INSERT INTO doctor_schedule (doctor_id, room_id, work_date, start_time, end_time, max_patients) VALUES
(1, 1, CURDATE(), '08:00:00', '12:00:00', 30),
(1, 1, CURDATE(), '14:00:00', '17:00:00', 30),
(2, 2, CURDATE(), '08:00:00', '12:00:00', 30),
(3, 3, CURDATE(), '08:00:00', '17:00:00', 40);

-- 插入系统用户（密码都是：123456，实际使用时应加密）
INSERT INTO system_user (username, password, user_role, emp_id) VALUES
('admin', '123456', '管理员', 6),
('receptionist', '123456', '前台', 5);

INSERT INTO system_user (username, password, user_role) VALUES
('patient_demo', '123456', '患者');
