# -*- coding: utf-8 -*-
"""
社区医院门诊管理系统 - 主程序 (SQLite版本)
"""

from flask import Flask, render_template, request, jsonify, session
import sqlite3
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'hospital_management_secret_key_2026'

# SQLite数据库文件路径
DB_FILE = 'hospital.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

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

@app.route('/help')
def firewall_guide():
    """防火墙配置指南"""
    return render_template('firewall_guide.html')

@app.route('/network-test')
def network_test():
    """网络测试页面"""
    return render_template('network_test.html')

@app.route('/api/get_client_ip')
def get_client_ip():
    """获取客户端IP"""
    try:
        # 尝试获取真实IP（考虑代理）
        if request.environ.get('HTTP_X_FORWARDED_FOR'):
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.environ.get('REMOTE_ADDR', 'Unknown')
        return jsonify({'success': True, 'ip': ip})
    except:
        return jsonify({'success': False, 'ip': 'Unknown'})

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

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """获取科室列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT dept_id, dept_name, description FROM department")
        departments = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': departments})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/doctors', methods=['GET'])
def get_doctors_by_dept():
    """获取医生列表（可按科室筛选）"""
    try:
        dept_id = request.args.get('dept_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if dept_id:
            cursor.execute("""
                SELECT emp_id, emp_name, title, dept_id
                FROM employee
                WHERE dept_id = ? AND emp_type = '医生'
                ORDER BY emp_name
            """, (dept_id,))
        else:
            cursor.execute("""
                SELECT emp_id, emp_name, title, dept_id
                FROM employee
                WHERE emp_type = '医生'
                ORDER BY dept_id, emp_name
            """)
        
        doctors = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': doctors})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

# ==================== 患者功能 ====================

@app.route('/api/patient/appointment', methods=['POST'])
def create_appointment():
    """患者预约挂号"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO appointment (patient_name, phone, dept_id, doctor_id, appt_date, appt_time, status)
            VALUES (?, ?, ?, ?, ?, ?, '待到院')
        """, (
            data['patient_name'],
            data['phone'],
            data['dept_id'],
            data.get('doctor_id'),
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
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.appt_id, a.patient_name, a.phone, d.dept_name,
                   a.appt_date, a.appt_time, a.status, a.created_at
            FROM appointment a
            JOIN department d ON a.dept_id = d.dept_id
            WHERE a.phone = ?
            ORDER BY a.appt_date DESC, a.appt_time DESC
        """, (phone,))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': appointments})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

# ==================== 前台功能 ====================

@app.route('/api/receptionist/register', methods=['POST'])
def register_visit():
    """患者到院登记"""
    try:
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查患者是否存在
        cursor.execute("SELECT patient_id FROM patient WHERE phone = ?", (data['phone'],))
        patient = cursor.fetchone()
        
        if patient:
            patient = dict(patient)
            patient_id = patient['patient_id']
        else:
            # 创建新患者
            cursor.execute("""
                INSERT INTO patient (patient_name, gender, id_card, phone)
                VALUES (?, ?, ?, ?)
            """, (data['patient_name'], data.get('gender'), data.get('id_card'), data['phone']))
            patient_id = cursor.lastrowid
        
        # 创建就诊记录
        cursor.execute("""
            INSERT INTO visit (patient_id, dept_id, doctor_id, room_id, visit_date, visit_time, status)
            VALUES (?, ?, ?, ?, date('now'), time('now'), '等待就诊')
        """, (patient_id, data['dept_id'], data.get('doctor_id'), data['room_id']))
        
        visit_id = cursor.lastrowid
        
        # 如果是预约患者，更新预约状态
        if data.get('appt_id'):
            cursor.execute("""
                UPDATE appointment SET status = '已到院' WHERE appt_id = ?
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

@app.route('/api/receptionist/patients', methods=['GET'])
def get_patients():
    """查询患者信息"""
    try:
        keyword = request.args.get('keyword', '').strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if keyword:
            # 按关键词搜索
            cursor.execute("""
                SELECT patient_id, patient_name, gender, phone, id_card, address, created_at as registration_date
                FROM patient
                WHERE patient_name LIKE ? OR phone LIKE ? OR id_card LIKE ?
                ORDER BY created_at DESC
                LIMIT 50
            """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        else:
            # 获取全部患者（最近50个）
            cursor.execute("""
                SELECT patient_id, patient_name, gender, phone, id_card, address, created_at as registration_date
                FROM patient
                ORDER BY created_at DESC
                LIMIT 50
            """)
        
        patients = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': patients})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/receptionist/patient/<int:patient_id>/visits', methods=['GET'])
def get_patient_visits(patient_id):
    """获取患者就诊记录"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取患者信息
        cursor.execute("""
            SELECT patient_id, patient_name, gender, phone, id_card, address
            FROM patient
            WHERE patient_id = ?
        """, (patient_id,))
        
        patient = cursor.fetchone()
        if not patient:
            return jsonify({'success': False, 'message': '患者不存在'})
        
        patient = dict(patient)
        
        # 获取就诊记录
        cursor.execute("""
            SELECT v.visit_id, v.visit_date, v.visit_time, v.status,
                   d.dept_name,
                   e.emp_name as doctor_name,
                   c.room_name,
                   v.diagnosis
            FROM visit v
            LEFT JOIN department d ON v.dept_id = d.dept_id
            LEFT JOIN employee e ON v.doctor_id = e.emp_id
            LEFT JOIN clinic_room c ON v.room_id = c.room_id
            WHERE v.patient_id = ?
            ORDER BY v.visit_date DESC, v.visit_time DESC
        """, (patient_id,))
        
        visits = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'patient': patient,
            'visits': visits
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/receptionist/visits', methods=['GET'])
def get_visits():
    """查询就诊信息"""
    try:
        status = request.args.get('status')
        date_filter = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT v.visit_id, p.patient_name, d.dept_name, 
                   cr.room_name, v.visit_time, v.status,
                   e.emp_name as doctor_name
            FROM visit v
            JOIN patient p ON v.patient_id = p.patient_id
            JOIN department d ON v.dept_id = d.dept_id
            JOIN clinic_room cr ON v.room_id = cr.room_id
            LEFT JOIN employee e ON v.doctor_id = e.emp_id
            WHERE v.visit_date = ?
        """
        params = [date_filter]
        
        if status:
            query += " AND v.status = ?"
            params.append(status)
        
        query += " ORDER BY v.visit_time DESC"
        
        cursor.execute(query, params)
        visits = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': visits})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/receptionist/visit_info', methods=['GET'])
def get_visit_info():
    """获取就诊信息用于结算"""
    try:
        visit_id = request.args.get('visit_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT v.visit_id, v.patient_id, p.patient_name, p.phone,
                   d.dept_name, cr.room_name, v.visit_date, v.visit_time
            FROM visit v
            JOIN patient p ON v.patient_id = p.patient_id
            JOIN department d ON v.dept_id = d.dept_id
            JOIN clinic_room cr ON v.room_id = cr.room_id
            WHERE v.visit_id = ?
        """, (visit_id,))
        
        visit = cursor.fetchone()
        if visit:
            visit = dict(visit)
        
        cursor.close()
        conn.close()
        
        if visit:
            return jsonify({'success': True, 'data': visit})
        else:
            return jsonify({'success': False, 'message': '未找到就诊记录'})
        
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
            VALUES (?, ?, ?, ?, ?, ?, '已支付', datetime('now'), ?)
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
            UPDATE visit SET status = '已离院' WHERE visit_id = ?
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
        cursor = conn.cursor()
        
        if dept_id:
            cursor.execute("""
                SELECT room_id, room_name, status 
                FROM clinic_room 
                WHERE dept_id = ? AND status = '开放'
            """, (dept_id,))
        else:
            cursor.execute("SELECT room_id, room_name, status FROM clinic_room WHERE status = '开放'")
        
        rooms = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': rooms})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

# ==================== 管理员功能 ====================

@app.route('/api/admin/dashboard', methods=['GET'])
def get_dashboard():
    """获取仪表板数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 今日就诊人次
        cursor.execute("""
            SELECT COUNT(*) as count FROM visit 
            WHERE visit_date = date('now')
        """)
        today_visits = cursor.fetchone()
        today_visits = dict(today_visits) if today_visits else {'count': 0}
        
        # 今日收入
        cursor.execute("""
            SELECT COALESCE(SUM(total_fee), 0) as revenue FROM billing 
            WHERE date(payment_time) = date('now') AND payment_status = '已支付'
        """)
        today_revenue = cursor.fetchone()
        today_revenue = dict(today_revenue) if today_revenue else {'revenue': 0}
        
        # 待就诊患者数
        cursor.execute("""
            SELECT COUNT(*) as count FROM visit 
            WHERE visit_date = date('now') AND status = '等待就诊'
        """)
        waiting_patients = cursor.fetchone()
        waiting_patients = dict(waiting_patients) if waiting_patients else {'count': 0}
        
        # 在职医生数
        cursor.execute("""
            SELECT COUNT(*) as count FROM employee 
            WHERE emp_type = '医生' AND work_status = '在职'
        """)
        active_doctors = cursor.fetchone()
        active_doctors = dict(active_doctors) if active_doctors else {'count': 0}
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'today_visits': today_visits['count'],
                'today_revenue': float(today_revenue['revenue']),
                'waiting_patients': waiting_patients['count'],
                'active_doctors': active_doctors['count']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/admin/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    try:
        stat_type = request.args.get('type', 'daily')
        start_date = request.args.get('start_date', date.today().strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', date.today().strftime('%Y-%m-%d'))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if stat_type == 'daily':
            # 按日期统计
            cursor.execute("""
                SELECT date(b.payment_time) as stat_date,
                       COUNT(DISTINCT v.visit_id) as visit_count,
                       SUM(b.total_fee) as total_revenue
                FROM billing b
                JOIN visit v ON b.visit_id = v.visit_id
                WHERE b.payment_status = '已支付'
                  AND date(b.payment_time) BETWEEN ? AND ?
                GROUP BY date(b.payment_time)
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
                  AND date(b.payment_time) BETWEEN ? AND ?
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
                  AND date(b.payment_time) BETWEEN ? AND ?
                GROUP BY e.emp_id, e.emp_name, d.dept_name
                ORDER BY total_revenue DESC
            """, (start_date, end_date))
        else:
            return jsonify({'success': False, 'message': '不支持的统计类型'})
        
        statistics = [dict(row) for row in cursor.fetchall()]
        
        # 格式化数据
        for stat in statistics:
            if 'total_revenue' in stat and stat['total_revenue']:
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
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.patient_id, p.patient_name, p.gender, p.phone, p.id_card,
                   COUNT(v.visit_id) as visit_count,
                   MAX(v.visit_date) as last_visit_date
            FROM patient p
            LEFT JOIN visit v ON p.patient_id = v.patient_id
            WHERE p.patient_name LIKE ? 
               OR p.phone LIKE ? 
               OR p.id_card LIKE ?
            GROUP BY p.patient_id
            ORDER BY last_visit_date DESC
            LIMIT 100
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        patients = [dict(row) for row in cursor.fetchall()]
        
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
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.emp_id, e.emp_name, e.emp_type, d.dept_name,
                   e.title, e.phone, e.work_status
            FROM employee e
            LEFT JOIN department d ON e.dept_id = d.dept_id
            ORDER BY e.emp_id
        """)
        
        employees = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': employees})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

@app.route('/api/admin/doctors', methods=['GET'])
def get_doctors():
    """获取医生列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.emp_id, e.emp_name, e.title, d.dept_name
            FROM employee e
            LEFT JOIN department d ON e.dept_id = d.dept_id
            WHERE e.emp_type = '医生' AND e.work_status = '在职'
            ORDER BY e.emp_id
        """)
        
        doctors = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': doctors})
        
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
            VALUES (?, ?, ?, ?, ?, ?)
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
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ds.schedule_id, e.emp_name as doctor_name, e.title,
                   d.dept_name, cr.room_name, ds.work_date,
                   ds.start_time, ds.end_time, ds.max_patients, ds.current_patients
            FROM doctor_schedule ds
            JOIN employee e ON ds.doctor_id = e.emp_id
            JOIN clinic_room cr ON ds.room_id = cr.room_id
            JOIN department d ON cr.dept_id = d.dept_id
            WHERE ds.work_date = ?
            ORDER BY ds.start_time
        """, (work_date,))
        
        schedules = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'data': schedules})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'查询失败：{str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
