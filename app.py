# -*- coding: utf-8 -*-
"""
社区医院门诊管理系统 - 主程序
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import pymysql
from datetime import datetime, date, timedelta
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = 'hospital_management_secret_key_2026'

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # 修改为你的MySQL用户名
    'password': '',  # 修改为你的MySQL密码
    'database': 'hospital_management',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def login_required(role=None):
    """登录验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': '请先登录'}), 401
            if role and session.get('user_role') != role:
                return jsonify({'success': False, 'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== 路由定义 ====================

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/login')
def login_page():
    """登录页面"""
    return render_template('login.html')

@app.route('/patient')
def patient_page():
    """患者页面"""
    return render_template('patient.html')

@app.route('/receptionist')
def receptionist_page():
    """前台页面"""
    return render_template('receptionist.html')

@app.route('/admin')
def admin_page():
    """管理员页面"""
    return render_template('admin.html')

# ==================== API接口 ====================

@app.route('/api/login', methods=['POST'])
def api_login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询用户
        cursor.execute("""
            SELECT user_id, username, user_role, emp_id, patient_id 
            FROM system_user 
            WHERE username = %s AND password = %s AND status = '启用'
        """, (username, password))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['user_role'] = user['user_role']
            session['emp_id'] = user['emp_id']
            session['patient_id'] = user['patient_id']
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'role': user['user_role']
            })
        else:
            return jsonify({'success': False, 'message': '用户名或密码错误'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败：{str(e)}'})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True, 'message': '已退出登录'})

# ==================== 患者功能 ====================

@app.route('/api/patient/appointment', methods=['POST'])
def create_appointment():
    """患者预约挂号"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 插入预约信息
        cursor.execute("""
            INSERT INTO appointment (patient_name, phone, dept_id, appt_date, appt_time, status)
            VALUES (%s, %s, %s, %s, %s, '待到院')
        """, (
            data['patient_name'],
            data['phone'],
            data['dept_id'],
            data['appt_date'],
            data['appt_time']
        ))
        
        conn.commit()
        appt_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '预约成功',
            'appt_id': appt_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'预约失败：{str(e)}'})

@app.route('/api/patient/appointments', methods=['GET'])
def get_appointments():
    """查询预约信息"""
    try:
        phone = request.args.get('phone')
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT a.appt_id, a.patient_name, a.phone, d.dept_name,
                   a.appt_date, a.appt_time, a.status, a.created_at
            FROM appointment a
            JOIN department d ON a.dept_id = d.dept_id
            WHERE a.phone = %s
            ORDER BY a.appt_date DESC, a.appt_time DESC
        """, (phone,))
        
        appointments = cursor.fetchall()
        
        # 转换日期时间格式
        for appt in appointments:
            if appt['appt_date']:
                appt['appt_date'] = appt['appt_date'].strftime('%Y-%m-%d')
            if appt['appt_time']:
                appt['appt_time'] = str(appt['appt_time'])
            if appt['created_at']:
                appt['created_at'] = appt['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': appointments})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """获取科室列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("SELECT dept_id, dept_name, description FROM department")
        departments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': departments})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

# ==================== 前台功能 ====================

@app.route('/api/receptionist/register', methods=['POST'])
def register_visit():
    """患者到院登记"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 检查患者是否存在，不存在则创建
        cursor.execute("SELECT patient_id FROM patient WHERE phone = %s", (data['phone'],))
        patient = cursor.fetchone()
        
        if not patient:
            # 创建新患者
            cursor.execute("""
                INSERT INTO patient (patient_name, gender, id_card, phone)
                VALUES (%s, %s, %s, %s)
            """, (data['patient_name'], data.get('gender'), data.get('id_card'), data['phone']))
            patient_id = cursor.lastrowid
        else:
            patient_id = patient['patient_id']
        
        # 创建就诊记录
        cursor.execute("""
            INSERT INTO visit (patient_id, dept_id, room_id, visit_date, visit_time, status)
            VALUES (%s, %s, %s, CURDATE(), CURTIME(), '等待就诊')
        """, (patient_id, data['dept_id'], data['room_id']))
        
        visit_id = cursor.lastrowid
        
        # 如果是预约患者，更新预约状态
        if data.get('appt_id'):
            cursor.execute("""
                UPDATE appointment SET status = '已到院' WHERE appt_id = %s
            """, (data['appt_id'],))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '登记成功',
            'visit_id': visit_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'登记失败：{str(e)}'})

@app.route('/api/receptionist/visits', methods=['GET'])
def get_visits():
    """查询就诊信息"""
    try:
        status = request.args.get('status')
        date_filter = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        query = """
            SELECT v.visit_id, p.patient_name, d.dept_name, 
                   cr.room_name, v.visit_time, v.status,
                   e.emp_name as doctor_name
            FROM visit v
            JOIN patient p ON v.patient_id = p.patient_id
            JOIN department d ON v.dept_id = d.dept_id
            JOIN clinic_room cr ON v.room_id = cr.room_id
            LEFT JOIN employee e ON v.doctor_id = e.emp_id
            WHERE v.visit_date = %s
        """
        params = [date_filter]
        
        if status:
            query += " AND v.status = %s"
            params.append(status)
        
        query += " ORDER BY v.visit_time DESC"
        
        cursor.execute(query, params)
        visits = cursor.fetchall()
        
        # 格式化时间
        for visit in visits:
            if visit['visit_time']:
                visit['visit_time'] = str(visit['visit_time'])
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': visits})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/receptionist/billing', methods=['POST'])
def create_billing():
    """创建费用账单"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        total_fee = float(data['total_fee'])
        insurance_fee = float(data.get('insurance_fee', 0))
        self_fee = total_fee - insurance_fee
        
        # 创建账单
        cursor.execute("""
            INSERT INTO billing (visit_id, patient_id, total_fee, insurance_fee, 
                                self_fee, payment_method, payment_status, payment_time, operator_id)
            VALUES (%s, %s, %s, %s, %s, %s, '已支付', NOW(), %s)
        """, (
            data['visit_id'],
            data['patient_id'],
            total_fee,
            insurance_fee,
            self_fee,
            data['payment_method'],
            session.get('emp_id')
        ))
        
        # 更新就诊状态为已离院
        cursor.execute("""
            UPDATE visit SET status = '已离院' WHERE visit_id = %s
        """, (data['visit_id'],))
        
        conn.commit()
        bill_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '缴费成功',
            'bill_id': bill_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'缴费失败：{str(e)}'})

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """获取诊室列表"""
    try:
        dept_id = request.args.get('dept_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if dept_id:
            cursor.execute("""
                SELECT room_id, room_name, status 
                FROM clinic_room 
                WHERE dept_id = %s AND status = '开放'
            """, (dept_id,))
        else:
            cursor.execute("SELECT room_id, room_name, status FROM clinic_room WHERE status = '开放'")
        
        rooms = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': rooms})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

# ==================== 管理员功能 ====================

@app.route('/api/admin/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    try:
        stat_type = request.args.get('type', 'daily')
        start_date = request.args.get('start_date', date.today().strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        if stat_type == 'daily':
            # 按日期统计
            cursor.execute("""
                SELECT DATE(b.payment_time) as stat_date,
                       COUNT(DISTINCT v.visit_id) as visit_count,
                       SUM(b.total_fee) as total_revenue
                FROM billing b
                JOIN visit v ON b.visit_id = v.visit_id
                WHERE b.payment_status = '已支付'
                  AND DATE(b.payment_time) BETWEEN %s AND %s
                GROUP BY DATE(b.payment_time)
                ORDER BY stat_date
            """, (start_date, end_date))
            
        elif stat_type == 'department':
            # 按科室统计
            cursor.execute("""
                SELECT d.dept_name,
                       COUNT(DISTINCT v.visit_id) as visit_count,
                       SUM(b.total_fee) as total_revenue
                FROM billing b
                JOIN visit v ON b.visit_id = v.visit_id
                JOIN department d ON v.dept_id = d.dept_id
                WHERE b.payment_status = '已支付'
                  AND DATE(b.payment_time) BETWEEN %s AND %s
                GROUP BY d.dept_id, d.dept_name
                ORDER BY total_revenue DESC
            """, (start_date, end_date))
            
        elif stat_type == 'doctor':
            # 按医生统计
            cursor.execute("""
                SELECT e.emp_name,
                       d.dept_name,
                       COUNT(DISTINCT v.visit_id) as visit_count,
                       SUM(b.total_fee) as total_revenue
                FROM billing b
                JOIN visit v ON b.visit_id = v.visit_id
                JOIN employee e ON v.doctor_id = e.emp_id
                JOIN department d ON v.dept_id = d.dept_id
                WHERE b.payment_status = '已支付'
                  AND DATE(b.payment_time) BETWEEN %s AND %s
                GROUP BY e.emp_id, e.emp_name, d.dept_name
                ORDER BY total_revenue DESC
            """, (start_date, end_date))
        
        statistics = cursor.fetchall()
        
        # 格式化数据
        for stat in statistics:
            if 'stat_date' in stat and stat['stat_date']:
                stat['stat_date'] = stat['stat_date'].strftime('%Y-%m-%d')
            if 'total_revenue' in stat:
                stat['total_revenue'] = float(stat['total_revenue'])
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': statistics})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'统计失败：{str(e)}'})

@app.route('/api/admin/patients', methods=['GET'])
def search_patients():
    """查询患者信息"""
    try:
        keyword = request.args.get('keyword', '')
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT p.patient_id, p.patient_name, p.gender, p.phone, p.id_card,
                   COUNT(v.visit_id) as visit_count,
                   MAX(v.visit_date) as last_visit_date
            FROM patient p
            LEFT JOIN visit v ON p.patient_id = v.patient_id
            WHERE p.patient_name LIKE %s 
               OR p.phone LIKE %s 
               OR p.id_card LIKE %s
            GROUP BY p.patient_id
            ORDER BY last_visit_date DESC
            LIMIT 100
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        patients = cursor.fetchall()
        
        # 格式化日期
        for patient in patients:
            if patient['last_visit_date']:
                patient['last_visit_date'] = patient['last_visit_date'].strftime('%Y-%m-%d')
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': patients})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/admin/employees', methods=['GET'])
def get_employees():
    """查询员工信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT e.emp_id, e.emp_name, e.emp_type, d.dept_name,
                   e.title, e.phone, e.work_status
            FROM employee e
            LEFT JOIN department d ON e.dept_id = d.dept_id
            ORDER BY e.emp_id
        """)
        
        employees = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': employees})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/admin/schedule', methods=['POST'])
def create_schedule():
    """创建医生排班"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO doctor_schedule (doctor_id, room_id, work_date, start_time, end_time, max_patients)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data['doctor_id'],
            data['room_id'],
            data['work_date'],
            data['start_time'],
            data['end_time'],
            data.get('max_patients', 30)
        ))
        
        conn.commit()
        schedule_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '排班创建成功',
            'schedule_id': schedule_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'排班失败：{str(e)}'})

@app.route('/api/admin/schedules', methods=['GET'])
def get_schedules():
    """查询排班信息"""
    try:
        work_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT ds.schedule_id, e.emp_name as doctor_name, e.title,
                   d.dept_name, cr.room_name, ds.work_date,
                   ds.start_time, ds.end_time, ds.max_patients, ds.current_patients
            FROM doctor_schedule ds
            JOIN employee e ON ds.doctor_id = e.emp_id
            JOIN clinic_room cr ON ds.room_id = cr.room_id
            JOIN department d ON cr.dept_id = d.dept_id
            WHERE ds.work_date = %s
            ORDER BY ds.start_time
        """, (work_date,))
        
        schedules = cursor.fetchall()
        
        # 格式化数据
        for schedule in schedules:
            if schedule['work_date']:
                schedule['work_date'] = schedule['work_date'].strftime('%Y-%m-%d')
            if schedule['start_time']:
                schedule['start_time'] = str(schedule['start_time'])
            if schedule['end_time']:
                schedule['end_time'] = str(schedule['end_time'])
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': schedules})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/admin/doctors', methods=['GET'])
def get_doctors():
    """获取医生列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT e.emp_id, e.emp_name, e.title, d.dept_name
            FROM employee e
            LEFT JOIN department d ON e.dept_id = d.dept_id
            WHERE e.emp_type = '医生' AND e.work_status = '在职'
            ORDER BY e.emp_id
        """)
        
        doctors = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': doctors})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
