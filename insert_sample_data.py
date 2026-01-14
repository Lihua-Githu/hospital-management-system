# -*- coding: utf-8 -*-
"""
插入患者样本数据
"""
import sqlite3
from datetime import datetime, timedelta
import random

def insert_sample_patients():
    conn = sqlite3.connect('hospital.db')
    cursor = conn.cursor()
    
    # 患者样本数据
    patients = [
        ('王建国', '男', '440100198001011234', '13800138001'),
        ('李明华', '女', '440100198502152345', '13800138002'),
        ('张伟强', '男', '440100199003203456', '13800138003'),
        ('刘芳芳', '女', '440100198807254567', '13800138004'),
        ('陈浩然', '男', '440100199512015678', '13800138005'),
        ('赵丽娜', '女', '440100198209106789', '13800138006'),
        ('孙晓东', '男', '440100199106177890', '13800138007'),
        ('周美玲', '女', '440100198704088901', '13800138008'),
        ('吴国栋', '男', '440100199208299012', '13800138009'),
        ('郑雅琪', '女', '440100199901120123', '13800138010'),
        ('黄志远', '男', '440100198305211234', '13800138011'),
        ('林思婷', '女', '440100199410132345', '13800138012'),
        ('何俊杰', '男', '440100198611243456', '13800138013'),
        ('许梦洁', '女', '440100199707054567', '13800138014'),
        ('冯建华', '男', '440100198108165678', '13800138015')
    ]
    
    print("正在插入患者数据...")
    patient_ids = []
    
    for name, gender, id_card, phone in patients:
        try:
            cursor.execute("""
                INSERT INTO patient (patient_name, gender, id_card, phone)
                VALUES (?, ?, ?, ?)
            """, (name, gender, id_card, phone))
            patient_ids.append(cursor.lastrowid)
            print(f"  ✓ 已添加患者: {name}")
        except sqlite3.IntegrityError:
            # 如果电话已存在，获取patient_id
            cursor.execute("SELECT patient_id FROM patient WHERE phone = ?", (phone,))
            result = cursor.fetchone()
            if result:
                patient_ids.append(result[0])
                print(f"  - 患者已存在: {name}")
    
    conn.commit()
    
    # 为部分患者创建历史就诊记录
    print("\n正在创建历史就诊记录...")
    dept_ids = [1, 2, 3, 4, 5]  # 5个科室
    room_ids = [1, 2, 3, 4, 5]  # 5个诊室
    
    visit_count = 0
    for i in range(min(10, len(patient_ids))):  # 为前10个患者创建就诊记录
        patient_id = patient_ids[i]
        # 每个患者1-3次就诊记录
        num_visits = random.randint(1, 3)
        
        for j in range(num_visits):
            # 随机日期（过去30天内）
            days_ago = random.randint(1, 30)
            visit_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            visit_time = f"{random.randint(8, 16):02d}:{random.randint(0, 59):02d}:00"
            
            dept_id = random.choice(dept_ids)
            room_id = random.choice(room_ids)
            doctor_id = random.randint(1, 3)  # 假设有3个医生
            
            cursor.execute("""
                INSERT INTO visit (patient_id, dept_id, room_id, doctor_id, 
                                 visit_date, visit_time, status)
                VALUES (?, ?, ?, ?, ?, ?, '已离院')
            """, (patient_id, dept_id, room_id, doctor_id, visit_date, visit_time))
            
            visit_id = cursor.lastrowid
            
            # 为已完成的就诊创建账单
            total_fee = random.randint(50, 500)
            insurance_fee = int(total_fee * random.uniform(0.5, 0.8))
            self_fee = total_fee - insurance_fee
            payment_method = random.choice(['现金', '医保卡', '银行卡', '微信', '支付宝'])
            
            cursor.execute("""
                INSERT INTO billing (visit_id, patient_id, total_fee, insurance_fee, 
                                   self_fee, payment_method, payment_status, 
                                   payment_time, operator_id)
                VALUES (?, ?, ?, ?, ?, ?, '已支付', ?, 2)
            """, (visit_id, patient_id, total_fee, insurance_fee, self_fee, 
                  payment_method, f"{visit_date} {visit_time}"))
            
            visit_count += 1
    
    conn.commit()
    print(f"  ✓ 已创建 {visit_count} 条就诊记录")
    
    # 创建一些预约记录
    print("\n正在创建预约记录...")
    appt_count = 0
    for i in range(min(5, len(patient_ids))):
        patient_id = patient_ids[i + 10] if i + 10 < len(patient_ids) else patient_ids[i]
        
        # 获取患者信息
        cursor.execute("SELECT patient_name, phone FROM patient WHERE patient_id = ?", 
                      (patient_id,))
        patient = cursor.fetchone()
        
        if patient:
            # 未来几天的预约
            days_ahead = random.randint(0, 7)
            appt_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            appt_time = f"{random.randint(8, 16):02d}:{random.randint(0, 59):02d}"
            
            dept_id = random.choice(dept_ids)
            status = '待到院' if days_ahead > 0 else '已到院'
            
            cursor.execute("""
                INSERT INTO appointment (patient_name, phone, dept_id, 
                                       appt_date, appt_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (patient[0], patient[1], dept_id, appt_date, appt_time, status))
            
            appt_count += 1
    
    conn.commit()
    print(f"  ✓ 已创建 {appt_count} 条预约记录")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ 样本数据插入完成！")
    print("="*50)
    print(f"患者总数: {len(patients)}")
    print(f"就诊记录: {visit_count}")
    print(f"预约记录: {appt_count}")
    print("\n现在可以在系统中查看这些数据了！")

if __name__ == '__main__':
    insert_sample_patients()
