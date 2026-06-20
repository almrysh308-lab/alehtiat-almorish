#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Client for Seha Website Integration
عميل API لربط البوت بموقع صحة
"""

import requests
import json
import logging
import random
import time
from datetime import datetime
from config_updated import API_FULL_URL, BOT_API_KEY

# إعداد التسجيل
logger = logging.getLogger(__name__)

def normalize_date_to_ddmmyyyy(date_str):
    """تحويل أي صيغة تاريخ إلى DD-MM-YYYY
    يدعم: DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY, YYYY/MM/DD
    """
    if not date_str:
        return date_str
    try:
        # Try with dash separator
        for sep in ['-', '/', '.']:
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    # Check if year is first (YYYY-MM-DD)
                    if len(parts[0]) == 4:
                        # YYYY-MM-DD -> DD-MM-YYYY
                        return f"{parts[2]}-{parts[1]}-{parts[0]}"
                    else:
                        # Already DD-MM-YYYY, just normalize separator
                        return f"{parts[0]}-{parts[1]}-{parts[2]}"
        return date_str
    except Exception:
        return date_str

def parse_date_components(date_str):
    """تحليل التاريخ وإرجاع (day, month, year) بغض النظر عن الصيغة"""
    if not date_str:
        return None
    try:
        for sep in ['-', '/', '.']:
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    if len(parts[0]) == 4:
                        # YYYY-MM-DD
                        return (int(parts[2]), int(parts[1]), int(parts[0]))
                    else:
                        # DD-MM-YYYY
                        return (int(parts[0]), int(parts[1]), int(parts[2]))
        return None
    except Exception:
        return None

def calculate_days(admission_date, discharge_date):
    """حساب عدد الأيام بين تاريخين - يدعم صيغ مختلفة"""
    try:
        admission_parsed = parse_date_components(admission_date)
        discharge_parsed = parse_date_components(discharge_date)
        
        if admission_parsed and discharge_parsed:
            admission_dt = datetime(admission_parsed[2], admission_parsed[1], admission_parsed[0])
            discharge_dt = datetime(discharge_parsed[2], discharge_parsed[1], discharge_parsed[0])
            
            days = (discharge_dt - admission_dt).days + 1
            return max(1, days)
        else:
            return 1
    except Exception as e:
        logger.error(f"خطأ في حساب الأيام: {e}")
        return 1

def generate_leave_id(id_number, admission_date, discharge_date):
    """توليد رمز الإجازة GSL فريد لكل إصدار، حتى لو كانت البيانات متطابقة.
    البادئة الإجبارية: GSL (بصرف النظر عن نوع المنشأة)
    النظام يدعم توليد أكثر من معرف إجازة فريد - كل سجل جديد يولد GSL مختلف تماماً.

    الآلية:
    - تُستخدم آخر 4 أرقام من رقم الهوية + أرقام من تاريخ الدخول + أرقام من تاريخ الخروج
      كأساس منطقي يربط الرمز بالبيانات.
    - يُضاف جزء عشوائي (4 أرقام) + طابع زمني (آخر 3 أرقام من الملي ثانية) لضمان
      أن كل رمز جديد يختلف تماماً عن سابقه، حتى لو أُدخلت نفس البيانات بالضبط.
    - الطول النهائي: 11 رقماً بعد البادئة GSL.
    """
    try:
        # Normalize dates to DD-MM-YYYY first for consistent digit extraction
        admission_normalized = normalize_date_to_ddmmyyyy(admission_date)
        discharge_normalized = normalize_date_to_ddmmyyyy(discharge_date)

        id_part = id_number[-4:] if len(id_number) >= 4 else (id_number or '0000')
        admission_nums = ''.join(filter(str.isdigit, admission_normalized))[-3:].ljust(3, '0')
        discharge_nums = ''.join(filter(str.isdigit, discharge_normalized))[-4:].ljust(4, '0')

        # ✅ جزء عشوائي + طابع زمني لضمان التفرّد التام لكل إصدار
        # 4 أرقام عشوائية (1000-9999) + آخر 3 أرقام من الملي ثانية الحالية
        random_part = f"{random.randint(1000, 9999)}"
        time_part = f"{int(time.time() * 1000) % 1000:03d}"
        unique_part = random_part + time_part  # 4 + 3 = 7 أرقام

        # التركيب النهائي: discharge(4) + admission(3) + id(4) = 11 رقماً
        # ثم نُدمج جزء التفرّد في المواضع الزوجية باستبدال بسيط دون تغيير الطول:
        base = (discharge_nums + admission_nums + id_part)[:11].ljust(11, '0')
        # استبدال آخر 7 أرقام بجزء التفرّد لضمان اختلاف الرمز لكل إصدار
        leave_number = base[:4] + unique_part  # 4 + 7 = 11 رقماً
        leave_number = leave_number[:11].ljust(11, '0')

        logger.info(f"تم توليد رمز إجازة فريد: GSL{leave_number} (الأساس: {base})")
        return f"GSL{leave_number}"
    except Exception as e:
        logger.error(f"خطأ في توليد رمز الإجازة: {e}")
        # حتى في حالة الخطأ، نُولّد رمزاً عشوائياً فريداً
        random_part = f"{random.randint(10000000, 99999999)}"
        return f"GSL260{random_part}"

def convert_date_format(date_str):
    """تحويل التاريخ من DD-MM-YYYY إلى YYYY-MM-DD لقاعدة البيانات
    يتعرف تلقائياً على الصيغة ويتجنب التحويل الخاطئ
    """
    if not date_str:
        return date_str
    try:
        # First normalize to DD-MM-YYYY
        normalized = normalize_date_to_ddmmyyyy(date_str)
        # Then convert DD-MM-YYYY to YYYY-MM-DD
        parts = normalized.split('-')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
        return date_str
    except Exception:
        return date_str

def send_leave_data_to_api(user_data):
    """إرسال بيانات الإجازة إلى API الموقع"""
    try:
        # ✅ نستخدم رمز الإجازة المُمرّر من user_data إن وُجد (مما يضمن تطابقه مع
        # الرمز المعروض في ملف PDF)، وإلا نولّد رمزاً جديداً فريداً هنا.
        # كل استدعاء يولّد رمزاً مختلفاً عن سابقه بفضل العنصر العشوائي + الطابع الزمني.
        leave_id = user_data.get('leave_id')
        if not leave_id or not str(leave_id).strip().startswith('GSL'):
            leave_id = generate_leave_id(
                user_data.get('id_number', ''),
                user_data.get('admission_date_gregorian', ''),
                user_data.get('discharge_date_gregorian', '')
            )
        else:
            leave_id = str(leave_id).strip()
        
        day_count = calculate_days(
            user_data.get('admission_date_gregorian', ''),
            user_data.get('discharge_date_gregorian', '')
        )
        
        report_date = convert_date_format(user_data.get('issue_date_gregorian', ''))
        entry_date = convert_date_format(user_data.get('admission_date_gregorian', ''))
        exit_date = convert_date_format(user_data.get('discharge_date_gregorian', ''))
        
        # إعداد البيانات للإرسال - مطابق لـ Node.js backend
        api_data = {
            'leaveNumber': leave_id,
            'idNumber': user_data.get('id_number', ''),
            'name': user_data.get('patient_name_ar', ''),
            'nameEn': user_data.get('patient_name_en', ''),
            'reportDate': report_date,
            'entryDate': entry_date,
            'exitDate': exit_date,
            'dayCount': day_count,
            'doctor': user_data.get('doctor_name_ar', ''),
            'doctorEn': user_data.get('doctor_name_en', ''),
            'jobTitle': user_data.get('position_ar', ''),
            'jobTitleEn': user_data.get('position_en', ''),
            'employer': user_data.get('employer_ar', ''),
            'employerEn': user_data.get('employer_en', ''),
            'nationality': user_data.get('nationality_ar', ''),
            'nationalityEn': user_data.get('nationality_en', ''),
            'hospitalName': user_data.get('hospital_name_ar', ''),
            'hospitalNameEn': user_data.get('hospital_name_en', ''),
            'licenseNumber': user_data.get('license_number', ''),
            'leaveType': 'sick'
        }
        
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'application/json',
            'X-API-Key': BOT_API_KEY
        }
        
        logger.info(f"إرسال البيانات إلى API: {API_FULL_URL}")
        logger.info(f"API Key: {BOT_API_KEY[:10]}...")
        logger.info(f"البيانات المرسلة: {json.dumps(api_data, ensure_ascii=False)}")
        
        response = requests.post(
            API_FULL_URL,
            json=api_data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logger.info(f"تم إرسال البيانات بنجاح: {result.get('message')}")
                return {
                    'success': True,
                    'message': 'تم حفظ بيانات الإجازة في النظام بنجاح',
                    'leave_id': leave_id,
                    'data': result.get('data', {})
                }
            else:
                logger.error(f"فشل في حفظ البيانات: {result.get('message')}")
                return {
                    'success': False,
                    'message': f"فشل في حفظ البيانات: {result.get('message')}",
                    'leave_id': leave_id
                }
        else:
            logger.error(f"خطأ HTTP {response.status_code}: {response.text}")
            return {
                'success': False,
                'message': f"خطأ في الاتصال بالخادم (HTTP {response.status_code})",
                'leave_id': leave_id
            }
            
    except requests.exceptions.ConnectionError:
        logger.error("فشل في الاتصال بالخادم")
        return {
            'success': False,
            'message': 'فشل في الاتصال بالخادم. تأكد من تشغيل الموقع.',
            'leave_id': leave_id if 'leave_id' in locals() else 'غير محدد'
        }
    except requests.exceptions.Timeout:
        logger.error("انتهت مهلة الاتصال")
        return {
            'success': False,
            'message': 'انتهت مهلة الاتصال بالخادم',
            'leave_id': leave_id if 'leave_id' in locals() else 'غير محدد'
        }
    except Exception as e:
        logger.error(f"خطأ غير متوقع في إرسال البيانات: {e}")
        return {
            'success': False,
            'message': f'خطأ غير متوقع: {str(e)}',
            'leave_id': leave_id if 'leave_id' in locals() else 'غير محدد'
        }

if __name__ == "__main__":
    test_data = {
        'id_number': '1234567890',
        'patient_name_ar': 'أحمد محمد السعيد',
        'patient_name_en': 'Ahmed Mohammed Al-Saeed',
        'issue_date_gregorian': '20-01-2025',
        'admission_date_gregorian': '18-01-2025',
        'discharge_date_gregorian': '20-01-2025',
        'doctor_name_ar': 'د. نبيل حنا نصر',
        'doctor_name_en': 'Dr. Nabil Hanna Nasr',
        'position_ar': 'طبيب عام',
        'position_en': 'General Practitioner',
        'employer_ar': 'طالب جامعي',
        'employer_en': 'University Student'
    }
    
    result = send_leave_data_to_api(test_data)
    print(f"نتيجة الاختبار: {json.dumps(result, ensure_ascii=False, indent=2)}")
