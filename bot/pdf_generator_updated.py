#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced PDF Generator for Seha Sick Leave Reports with Arabic Text Support - Updated Version
وحدة توليد تقارير الإجازة المرضية بصيغة PDF - النسخة المحدثة والمصححة
"""

import os
import re
import qrcode
from datetime import datetime
from fpdf import FPDF
from PIL import Image
from config_updated import *
from config_updated import QR_DISPLAY_URL
import arabic_reshaper
from bidi.algorithm import get_display

class SickLeavePDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format=(PDF_WIDTH, PDF_HEIGHT))
        self.set_auto_page_break(auto=False)
        # تحميل الخطوط
        self.load_fonts()

    def load_fonts(self):
        """تحميل الخطوط المطلوبة"""
        # خطوط عربية - أساسية ولا يمكن الاستغناء عنها
        if not os.path.exists(NOTO_SANS_ARABIC_BOLD):
            raise FileNotFoundError(f"ملف الخط العربي غير موجود: {NOTO_SANS_ARABIC_BOLD}")
        if not os.path.exists(NOTO_SANS_ARABIC_REGULAR):
            raise FileNotFoundError(f"ملف الخط العربي غير موجود: {NOTO_SANS_ARABIC_REGULAR}")
        
        self.add_font('NotoSansArabic-Bold', '', NOTO_SANS_ARABIC_BOLD)
        self.add_font('NotoSansArabic-Regular', '', NOTO_SANS_ARABIC_REGULAR)
        
        # خطوط إنجليزية - استخدام خط Times المدمج (Times-Bold / Times-Roman)
        # خط Times مدمج في fpdf2 ولا يحتاج ملفات خارجية
        print("✅ استخدام خط Times المدمج للنصوص الإنجليزية")

    def process_arabic_text(self, text):
        """معالجة النص العربي النقي (بدون أرقام/رموز مختلطة)"""
        if not text:
            return ""
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"خطأ في معالجة النص العربي: {e}")
            return text

    # ═══════════════════════════════════════════════════════════════
    # ✅ FIX: دالة safe_arabic_mixed - الإصدار المصحح نهائياً
    # تحافظ على الأقواس () والشرطات / و - والأرقام في أماكنها الصحيحة
    # ═══════════════════════════════════════════════════════════════
    def safe_arabic_mixed(self, text):
        """
        معالجة آمنة للنص المختلط (عربي + أرقام + رموز مثل: 2 يوم (1447-03-28 إلى 1447-03-29)).
        تستخدم arabic_reshaper + python-bidi لمعالجة النص كاملاً دون تقطيع أو عكس يدوي.
        """
        if not text:
            return ""
        try:
            # ✅ الخطوة 1: إعادة تشكيل الأحرف العربية للاتصال الصحيح (ربط الحروف)
            reshaped = arabic_reshaper.reshape(text)
            
            # ✅ الخطوة 2: تطبيق خوارزمية Unicode BiDi للترتيب البصري الصحيح
            # هذه الدالة تحافظ على مواضع الأرقام، الأقواس، الشرطات، والمسافات
            bidi_text = get_display(reshaped)
            
            return bidi_text
        except Exception as e:
            print(f"⚠️ خطأ في safe_arabic_mixed: {e}")
            # في حال حدوث خطأ، نرجع النص الأصلي لضمان عدم ضياع البيانات
            return text

    def add_header_images(self):
        """إضافة الصور والشعارات في الرأس"""
        try:
            if os.path.exists(SEHA_LOGO):
                self.image(SEHA_LOGO, x=11, y=12, w=56, h=26)
            if os.path.exists(GEOMETRIC_SHAPE):
                self.image(GEOMETRIC_SHAPE, x=191, y=12, w=94, h=40)
            if os.path.exists(KINGDOM_TEXT):
                self.image(KINGDOM_TEXT, x=100, y=13, w=94, h=45)
        except Exception as e:
            print(f"خطأ في إضافة صور الرأس: {e}")

    def add_titles(self):
        """إضافة العناوين الرئيسية"""
        self.set_font('NotoSansArabic-Bold', size=22)
        self.set_text_color(48, 109, 181)
        self.set_xy(116, 57)
        arabic_title = self.process_arabic_text('تقرير إجازة مرضية')
        self.cell(68, 10, arabic_title, align='C')

        self.set_font('Times', 'B', size=18)
        self.set_text_color(44, 62, 119)
        self.set_xy(123, 69)
        self.cell(52, 7, 'Sick Leave Report', align='C')

    def normalize_date_to_ddmmyyyy(self, date_str):
        """تحويل أي صيغة تاريخ إلى DD-MM-YYYY
        يدعم: DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY, YYYY/MM/DD
        """
        if not date_str:
            return date_str
        try:
            for sep in ['-', '/', '.']:
                if sep in date_str:
                    parts = date_str.split(sep)
                    if len(parts) == 3:
                        if len(parts[0]) == 4:
                            # YYYY-MM-DD -> DD-MM-YYYY
                            return f"{parts[2]}-{parts[1]}-{parts[0]}"
                        else:
                            # Already DD-MM-YYYY, normalize separator
                            return f"{parts[0]}-{parts[1]}-{parts[2]}"
            return date_str
        except Exception:
            return date_str

    def parse_date_components(self, date_str):
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

    def generate_leave_id(self, id_number, admission_date, discharge_date):
        """توليد رمز الإجازة - يطبع التواريخ أولاً إلى DD-MM-YYYY لضمان التوافق
        البادئة الإجبارية: GSL (بصرف النظر عن نوع المنشأة)
        النظام يدعم توليد أكثر من معرف إجازة فريد - كل محادثة بوت/كل سجل جديد يولد GSL مختلف
        """
        # Normalize dates to DD-MM-YYYY first for consistent digit extraction
        admission_normalized = self.normalize_date_to_ddmmyyyy(admission_date)
        discharge_normalized = self.normalize_date_to_ddmmyyyy(discharge_date)
        
        id_part = id_number[-4:] if len(id_number) >= 4 else id_number
        admission_nums = ''.join(filter(str.isdigit, admission_normalized))[-3:]
        discharge_nums = ''.join(filter(str.isdigit, discharge_normalized))[-4:]
        leave_number = (discharge_nums + admission_nums + id_part).ljust(11, '0')[:11]
        return f"GSL{leave_number}"

    def swap_date_format(self, date_str):
        """تحويل التاريخ من YYYY-MM-DD إلى DD-MM-YYYY والعكس"""
        if not date_str:
            return date_str
        try:
            # First normalize to DD-MM-YYYY
            normalized = self.normalize_date_to_ddmmyyyy(date_str)
            # If already normalized (same as input), swap to the other format
            parts = normalized.split('-')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
            return date_str
        except Exception:
            return date_str

    def calculate_duration(self, admission_date_hijri, discharge_date_hijri,
                          admission_date_gregorian, discharge_date_gregorian):
        """حساب مدة الإجازة - جميع التواريخ بصيغة DD-MM-YYYY (مثل 09-02-2026)
        ملاحظة: نستخدم علامة LRM (U+200E) حول التواريخ لمنع خوارزمية BiDi
        من عكس اتجاه الأرقام داخل السياق العربي (RTL).
        """
        # علامة Left-to-Right Mark لإجبار الأرقام على البقاء بترتيب LTR
        LRM = '\u200e'
        try:
            admission_parsed = self.parse_date_components(admission_date_gregorian)
            discharge_parsed = self.parse_date_components(discharge_date_gregorian)
            # تطبيع التواريخ الميلادية إلى DD-MM-YYYY مسبقاً
            admission_gregorian_normalized = self.normalize_date_to_ddmmyyyy(admission_date_gregorian)
            discharge_gregorian_normalized = self.normalize_date_to_ddmmyyyy(discharge_date_gregorian)
            # لف التواريخ بعلامات LRM لإجبارها على البقاء بصيغة DD-MM-YYYY في السياق العربي
            admission_lrm = f"{LRM}{admission_gregorian_normalized}{LRM}"
            discharge_lrm = f"{LRM}{discharge_gregorian_normalized}{LRM}"
            if admission_parsed and discharge_parsed:
                admission_dt = datetime(admission_parsed[2], admission_parsed[1], admission_parsed[0])
                discharge_dt = datetime(discharge_parsed[2], discharge_parsed[1], discharge_parsed[0])
                duration_days = (discharge_dt - admission_dt).days + 1

                # صيغة DD-MM-YYYY للمدة العربية (مع علامات LRM لمنع العكس)
                duration_ar = f"{duration_days} يوم  ( {admission_lrm} إلى {discharge_lrm} ) "

                day_word = "day" if duration_days == 1 else "days"
                # صيغة DD-MM-YYYY للمدة الإنجليزية أيضاً
                duration_en = f"{duration_days} {day_word}  ( {admission_gregorian_normalized} to {discharge_gregorian_normalized} ) "
                return duration_ar, duration_en
            else:
                duration_ar = f"1 يوم  ( {admission_lrm} إلى {discharge_lrm} ) "
                duration_en = f"1 day  ( {admission_gregorian_normalized} to {discharge_gregorian_normalized} ) "
                return duration_ar, duration_en
        except Exception as e:
            print(f"خطأ في حساب المدة: {e}")
            duration_ar = f"1 يوم  ( {admission_lrm} إلى {discharge_lrm} ) "
            duration_en = f"1 day  ( {admission_gregorian_normalized} to {discharge_gregorian_normalized} ) "
            return duration_ar, duration_en

    def add_table(self, data):
        """إضافة الجدول الرئيسي"""
        table_x = 12.5
        table_y = 85
        col_widths = [58, 83, 83, 48]
        row_heights = [15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        row_bg_colors = {
            1: (44, 62, 119),
            3: (247, 247, 247),
            5: (247, 247, 247),
            7: (247, 247, 247),
            9: (247, 247, 247),
        }

        leave_id = self.generate_leave_id(
            data.get('id_number', '1234567890'),
            data.get('admission_date_gregorian', '01-01-2025'),
            data.get('discharge_date_gregorian', '01-01-2025')
        )

        duration_ar, duration_en = self.calculate_duration(
            data.get('admission_date_hijri', '01-01-1446'),
            data.get('discharge_date_hijri', '01-01-1446'),
            data.get('admission_date_gregorian', '01-01-2025'),
            data.get('discharge_date_gregorian', '01-01-2025')
        )

        # معالجة النصوص العربية النقية
        processed_data = {}
        for key, value in data.items():
            if key.endswith('_ar') and value:
                processed_data[key] = self.process_arabic_text(value)
            else:
                processed_data[key] = value

        # ✅ توحيد جميع التواريخ الميلادية إلى صيغة DD-MM-YYYY (إجباري)
        admission_date_normalized = self.normalize_date_to_ddmmyyyy(
            data.get('admission_date_gregorian', '01-01-2025')
        )
        discharge_date_normalized = self.normalize_date_to_ddmmyyyy(
            data.get('discharge_date_gregorian', '01-01-2025')
        )
        issue_date_normalized = self.normalize_date_to_ddmmyyyy(
            data.get('issue_date_gregorian', '01-01-2025')
        )

        # ✅ معالجة جهة العمل الفارغة: مسافة بيضاء بدلاً من "فارغ" أو "-"
        employer_ar_value = data.get('employer_ar', '')
        employer_en_value = data.get('employer_en', '')
        # إذا كانت القيمة فارغة أو تحتوي على كلمات دالة على الفراغ، نعرض مسافة بيضاء
        empty_indicators = {'', 'غير محدد', 'فارغ', '-', 'None', 'none', 'null', 'NULL', 'Not Specified', 'N/A', 'n/a'}
        if not employer_ar_value or employer_ar_value.strip() in empty_indicators:
            employer_ar_value = ' '  # مسافة بيضاء فارغة
        else:
            employer_ar_value = self.process_arabic_text(employer_ar_value)
        if not employer_en_value or employer_en_value.strip() in empty_indicators:
            employer_en_value = ' '  # مسافة بيضاء فارغة

        # ✅ استخدام safe_arabic_mixed للنصوص المختلطة (المدة، رقم الهوية)
        duration_ar_processed = self.safe_arabic_mixed(duration_ar)
        id_label_processed = self.safe_arabic_mixed('رقم الهوية / الإقامة')

        table_data = [
            ['Leave ID', leave_id, '', self.process_arabic_text('رمز الإجازة')],
            ['Leave Duration', duration_en, duration_ar_processed, self.process_arabic_text('مدة الإجازة')],
            ['Admission Date', admission_date_normalized, admission_date_normalized,
             self.process_arabic_text('تاريخ الدخول')],
            ['Discharge Date', discharge_date_normalized, discharge_date_normalized,
             self.process_arabic_text('تاريخ الخروج')],
            ['Issue Date', issue_date_normalized, '',
             self.process_arabic_text('تاريخ إصدار التقرير')],
            ['Name', processed_data.get('patient_name_en', '').upper(), processed_data.get('patient_name_ar', ''),
             self.process_arabic_text('الاسم')],
            ['National ID / Iqama', processed_data.get('id_number', ''), '', id_label_processed],
            ['Nationality', processed_data.get('nationality_en', ''), processed_data.get('nationality_ar', ''),
             self.process_arabic_text('الجنسية')],
            ['Employer', employer_en_value, employer_ar_value,
             self.process_arabic_text('جهة العمل')],
            ["Practitioner Name", processed_data.get("doctor_name_en", "").upper(),
             processed_data.get("doctor_name_ar", ""), self.process_arabic_text("اسم الممارس")],
            ['Position', processed_data.get('position_en', ''), processed_data.get('position_ar', ''),
             self.process_arabic_text('المسمى الوظيفي')],
        ]

        current_y = table_y
        for row_idx, row_data in enumerate(table_data):
            current_x = table_x
            row_height = row_heights[row_idx]
            if row_idx in row_bg_colors:
                self.set_fill_color(*row_bg_colors[row_idx])
                fill = True
            else:
                fill = False
            for col_idx, cell_text in enumerate(row_data):
                col_width = col_widths[col_idx]
                if self.is_merged_cell(row_idx, col_idx):
                    current_x += col_width
                    continue
                actual_width = col_width
                if self.is_merge_start(row_idx, col_idx):
                    actual_width = col_widths[col_idx] + col_widths[col_idx + 1]
                self.set_draw_color(217, 217, 217)
                self.set_line_width(0.5)
                self.rect(current_x, current_y, actual_width, row_height, 'D' if not fill else 'DF')
                self.set_cell_font_and_color(row_idx, col_idx, cell_text)
                if cell_text:
                    if row_idx == 1 and col_idx == 2:
                        # خلية المدة العربية - عرض بخطين مع الحفاظ على ترتيب BiDi
                        self.render_mixed_font_cell_v2(current_x, current_y, actual_width, row_height, cell_text, (255, 255, 255))
                    elif (row_idx == 5 and col_idx in [1, 2]) or (row_idx == 9 and col_idx in [1, 2]):
                        # خلية الاسم أو الطبيب - عرض بسطرين إذا كان طويلاً
                        self.render_long_name_cell(current_x, current_y, actual_width, row_height, cell_text, row_idx, col_idx)
                    else:
                        self.set_xy(current_x, current_y)
                        align = self.get_cell_alignment(row_idx, col_idx)
                        self.cell(actual_width, row_height, cell_text, align=align)
                current_x += col_width
            current_y += row_height
        self.set_draw_color(217, 217, 217)
        self.set_line_width(0.5)
        self.line(153.5, 252, 153.5, 335)

    def is_merged_cell(self, row_idx, col_idx):
        if row_idx in [0, 4, 6] and col_idx == 2:
            return True
        return False

    def is_merge_start(self, row_idx, col_idx):
        if row_idx in [0, 4, 6] and col_idx == 1:
            return True
        return False

    def has_arabic_chars(self, text):
        """فحص هل النص يحتوي على حروف عربية"""
        if not text:
            return False
        for char in text:
            if '\u0600' <= char <= '\u06FF' or '\u0750' <= char <= '\u077F' or '\uFB50' <= char <= '\uFDFF' or '\uFE70' <= char <= '\uFEFF':
                return True
        return False

    def is_arabic_char(self, char):
        """فحص هل الحرف عربي"""
        return ('\u0600' <= char <= '\u06FF' or
                '\u0750' <= char <= '\u077F' or
                '\uFB50' <= char <= '\uFDFF' or
                '\uFE70' <= char <= '\uFEFF')

    def split_mixed_text(self, text):
        """تقسيم النص إلى أجزاء عربية وأجزاء أرقام/رموز"""
        if not text:
            return []
        segments = []
        current = ""
        current_is_arabic = None
        for char in text:
            is_ar = self.is_arabic_char(char)
            if current_is_arabic is None:
                current_is_arabic = is_ar
                current = char
            elif is_ar == current_is_arabic:
                current += char
            else:
                segments.append((current_is_arabic, current))
                current_is_arabic = is_ar
                current = char
        if current:
            segments.append((current_is_arabic, current))
        return segments

    def render_long_name_cell(self, x, y, width, height, text, row_idx, col_idx):
        """عرض خلية الاسم/الطبيب الطويل بسطرين مع توسيط عمودي وأفقي"""
        if not text:
            return
        # تحديد الخط والحجم
        self.set_cell_font_and_color(row_idx, col_idx, text)
        font_name = self.font_family
        font_style = self.font_style
        font_size = self.font_size_pt

        text_width = self.get_string_width(text)
        padding = 4  # مسافة أمان من الجوانب
        available_width = width - padding * 2

        if text_width <= available_width:
            # النص يكفي بسطر واحد - عرض عادي بالتوسيط
            self.set_xy(x, y)
            self.cell(width, height, text, align='C')
            return

        # النص طويل - تقسيمه إلى سطرين
        # البحث عن نقطة القطع المثالية: آخر مسافة قبل المنتصف أو بعد المنتصف
        words = text.split(' ')
        line1 = ''
        line2 = ''
        found_split = False

        for i in range(len(words), 0, -1):
            test_line = ' '.join(words[:i])
            if self.get_string_width(test_line) <= available_width:
                line1 = test_line
                line2 = ' '.join(words[i:])
                # إذا السطر الثاني طويل جداً، نقطع من منتصف الكلمة الأخيرة
                if self.get_string_width(line2) > available_width and line2:
                    # قطع الكلمة الأخيرة في السطر الأول بشرطة
                    last_word = words[i-1] if i > 0 else ''
                    # نحاول نقطع الكلمة الأخيرة
                    for cut in range(len(last_word)-1, 0, -1):
                        partial = last_word[:cut] + '-'
                        test_line1 = ' '.join(words[:i-1] + [partial]) if i > 1 else partial
                        remainder = last_word[cut:] + ' ' + ' '.join(words[i:]) if i < len(words) else last_word[cut:]
                        if self.get_string_width(test_line1) <= available_width and self.get_string_width(remainder) <= available_width:
                            line1 = test_line1
                            line2 = remainder
                            break
                found_split = True
                break

        if not found_split or not line2:
            # لا نجد نقطة قطع جيدة - عرض بسطر واحد
            self.set_xy(x, y)
            self.cell(width, height, text, align='C')
            return

        # حساب ارتفاع السطر وتوسيط عمودي
        line_height = height / 2
        # توسيط عمودي: حساب الإزاحة من الأعلى
        total_text_height = line_height * 2
        y_offset = y + (height - total_text_height) / 2

        # إعادة تعيين الخط (لأن get_string_width قد تغيره)
        self.set_font(font_name, font_style, size=font_size)

        # السطر الأول
        self.set_xy(x, y_offset)
        self.cell(width, line_height, line1, align='C')

        # السطر الثاني
        self.set_xy(x, y_offset + line_height)
        self.cell(width, line_height, line2, align='C')

    def render_mixed_font_cell_v2(self, x, y, width, height, text, color):
        """عرض خلية بخطين مع الحفاظ على ترتيب BiDi:
        الأرقام والأقواس بخط Times، الحروف العربية بخط NotoSansArabic
        يتجاهل علامات التحكم مثل LRM (U+200E) لأنها غير مرئية ولا تدعمها خط Times"""
        if not text:
            return
        # إزالة علامات التحكم غير المرئية (LRM, RLM, ZWJ, ZWNJ) لأنها لا تدعمها خط Times
        # وهي فقط لتوجيه BiDi ولا تظهر بصرياً
        import unicodedata
        clean_text = ''.join(
            char for char in text
            if unicodedata.category(char) != 'Cf'  # skip Format characters like LRM
        )
        text = clean_text
        # حساب العرض الكلي لكل حرف بالخط المناسب
        total_width = 0
        for char in text:
            if self.is_arabic_char(char):
                self.set_font('NotoSansArabic-Regular', size=13)
            else:
                self.set_font('Times', '', size=13)
            total_width += self.get_string_width(char)
        # توسيط أفقي
        start_x = x + (width - total_width) / 2
        self.set_xy(start_x, y)
        self.set_text_color(*color)
        # عرض كل حرف بالخط المناسب باستخدام write للحفاظ على الترتيب
        for char in text:
            if self.is_arabic_char(char):
                self.set_font('NotoSansArabic-Regular', size=13)
            else:
                self.set_font('Times', '', size=13)
            self.set_text_color(*color)
            self.write(height, char)

    def set_cell_font_and_color(self, row_idx, col_idx, text):
        blue_color = (54, 111, 181)
        dark_blue = (44, 62, 119)
        white_color = (255, 255, 255)
        if row_idx == 1:
            if col_idx in [0, 3]:
                if col_idx == 0:
                    self.set_font('Times', 'B', size=13)
                else:
                    # عنوان عربي - لا يحتوي أرقام عادة
                    self.set_font('NotoSansArabic-Bold', size=13)
                self.set_text_color(*white_color)
            else:
                if col_idx == 1:
                    self.set_font('Times', '', size=13)
                else:
                    # خلية رقم 2 صف 2 - مدة الإجازة العربية بدون غامق
                    self.set_font('NotoSansArabic-Regular', size=13)
                self.set_text_color(*white_color)
        elif col_idx == 0:
            self.set_font('Times', 'B', size=13)
            self.set_text_color(*blue_color)
        elif col_idx == 1:
            font_size = 13
            self.set_font('Times', '', size=font_size)
            self.set_text_color(*dark_blue)
        elif col_idx == 2:
            # إذا النص أرقام فقط (تواريخ، رقم هوية) استخدم Times مثل الجانب الإنجليزي
            # إذا النص يحتوي حروف عربية استخدم NotoSansArabic
            if self.has_arabic_chars(text):
                self.set_font('NotoSansArabic-Regular', size=13)
            else:
                self.set_font('Times', '', size=13)
            self.set_text_color(*dark_blue)
        elif col_idx == 3:
            self.set_font('NotoSansArabic-Bold', size=13)
            self.set_text_color(*blue_color)

    def get_cell_alignment(self, row_idx, col_idx):
        if row_idx in [0, 4, 6] and col_idx == 1:
            return 'C'
        elif col_idx == 1:
            if row_idx in [2, 3]:
                return 'C'
            else:
                return 'C'
        else:
            return 'C'

    def add_footer_elements(self, data):
        """إضافة عناصر التذييل"""
        try:
            # تطبيع تاريخ الإصدار إلى DD-MM-YYYY لبيانات QR
            issue_date_normalized = self.normalize_date_to_ddmmyyyy(data.get('issue_date_gregorian', ''))
            qr_data = f"{data.get('id_number', '')} - {self.generate_leave_id(data.get('id_number', ''), data.get('admission_date_gregorian', ''), data.get('discharge_date_gregorian', ''))} - {issue_date_normalized}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(QR_URL)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_path = f"{OUTPUT_DIR}/temp_qr.png"
            qr_img.save(qr_path)
            self.image(qr_path, x=60, y=262, w=42, h=40)

            self.set_font('NotoSansArabic-Bold', size=10)
            self.set_text_color(0, 0, 0)
            self.set_xy(45, 308)
            line1_text = self.process_arabic_text('للتحقق من بيانات التقرير يرجى التأكد من زيارة موقع منصة صحة')
            self.cell(72, 6, line1_text, align='C')

            self.set_xy(45, 314)
            line2_text = self.process_arabic_text('الرسمي')
            self.cell(72, 6, line2_text, align='C')

            self.set_font('Times', 'B', size=9)
            self.set_text_color(0, 0, 0)
            self.set_xy(45, 320)
            line3_text = "To check the report please visit Seha's offical website"
            self.cell(72, 6, line3_text, align='C')

            self.set_font('Times', 'B', size=11)
            self.set_text_color(0, 0, 255)
            self.set_xy(45, 326)
            display_url = (QR_DISPLAY_URL if QR_DISPLAY_URL else QR_URL).replace('https://', '').replace('http://', '')
            self.cell(72, 6, display_url, align='C', link=QR_URL)

            self.set_draw_color(0, 0, 255)
            self.set_line_width(0.1)
            link_start_x = 45 + (72 - self.get_string_width(display_url)) / 2
            link_end_x = link_start_x + self.get_string_width(display_url)
            self.line(link_start_x, 331, link_end_x, 331)

            if os.path.exists(qr_path):
                os.remove(qr_path)

            custom_logo = data.get('custom_logo')
            if custom_logo and os.path.exists(custom_logo):
                self.image(custom_logo, x=203, y=263, w=43, h=42)
            elif os.path.exists(HOSPITAL_LOGO):
                self.image(HOSPITAL_LOGO, x=203, y=263, w=43, h=42)

            hospital_name_ar = data.get('hospital_name_ar', 'مجمع عائلتي الطبي')
            hospital_name_en = data.get('hospital_name_en', 'My Family Medical Center')

            self.set_font('NotoSansArabic-Bold', size=12)
            self.set_text_color(0, 0, 0)
            self.set_xy(191, 305)
            processed_hospital_name = self.process_arabic_text(hospital_name_ar)
            self.cell(67, 10, processed_hospital_name, align='C')

            self.set_font('Times', 'B', size=12)
            self.set_text_color(0, 0, 0)
            self.set_xy(191, 315)
            self.cell(67, 10, hospital_name_en, align='C')

            # ✅ سطر رقم الترخيص: يُعرض فقط إذا وُجد رقم ترخيص في الاستمارة
            # إذا لم يوجد، لا يظهر السطر إطلاقاً
            license_number = data.get('license_number', '')
            # قائمة القيم الفارغة الدالة على عدم وجود رقم ترخيص
            empty_indicators = {'', 'غير محدد', 'فارغ', '-', 'None', 'none', 'null', 'NULL', 'Not Specified', 'N/A', 'n/a', 'undefined'}
            if license_number and isinstance(license_number, str) and license_number.strip() not in empty_indicators:
                # تنسيق السطر: "رقم الترخيص : <الرقم>"
                # النص العربي بخط NotoSansArabic-Bold، الرقم بخط Times-Bold
                license_label = self.process_arabic_text('رقم الترخيص')
                license_value = str(license_number).strip()
                # حساب عرض كل جزء لتوسيطهما معاً
                self.set_font('NotoSansArabic-Bold', size=12)
                label_w = self.get_string_width(license_label + ' : ')
                self.set_font('Times', 'B', size=12)
                value_w = self.get_string_width(license_value)
                total_w = label_w + value_w
                start_x = 191 + (67 - total_w) / 2
                # رسم الرقم (يسار) بخط Times-Bold
                self.set_font('Times', 'B', size=12)
                self.set_text_color(0, 0, 0)
                self.set_xy(start_x, 325)
                self.cell(value_w, 10, license_value, align='L')
                # رسم التسمية (يمين) بخط NotoSansArabic-Bold
                self.set_font('NotoSansArabic-Bold', size=12)
                self.set_text_color(0, 0, 0)
                self.set_xy(start_x + value_w, 325)
                self.cell(label_w, 10, license_label + ' : ', align='L')

            if os.path.exists(HEALTH_INFO_CENTER_LOGO):
                self.image(HEALTH_INFO_CENTER_LOGO, x=231, y=336, w=54, h=26)

            current_time = data.get('time', '6:23 AM')
            current_date = datetime.now().strftime('%A, %d %B %Y')
            self.set_font('Times', 'B', size=12)
            self.set_text_color(0, 0, 0)
            self.set_xy(11, 339)
            self.cell(20, 6, current_time, align='L')
            self.set_xy(11, 347)
            self.cell(47, 6, current_date, align='L')
        except Exception as e:
            print(f"خطأ في إضافة عناصر التذييل: {e}")


def generate_sick_leave_pdf(data, user_id):
    """توليد تقرير الإجازة المرضية"""
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        pdf = SickLeavePDF()
        pdf.add_page()
        pdf.add_header_images()
        pdf.add_titles()
        pdf.add_table(data)
        pdf.add_footer_elements(data)
        id_number = data.get('id_number', 'UNKNOWN')
        # تطبيع تاريخ الإصدار إلى DD-MM-YYYY لاستخدامه في اسم الملف/السجلات
        issue_date_raw = data.get('issue_date_gregorian', datetime.now().strftime('%d-%m-%Y'))
        issue_date = pdf.normalize_date_to_ddmmyyyy(issue_date_raw) if hasattr(pdf, 'normalize_date_to_ddmmyyyy') else issue_date_raw
        filename = "sickleave.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        pdf.output(filepath)
        return filepath
    except Exception as e:
        print(f"خطأ في توليد PDF: {e}")
        raise e


# ═══════════════════════════════════════════════════════════════
# ✅ قسم الاختبار للتحقق من إصلاح الأقواس والشرطات
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    pdf = SickLeavePDF()
    
    print("🔍 اختبار دالة safe_arabic_mixed بعد الإصلاح:\n")
    
    # اختبار 1: مدة الإجازة (المشكلة الرئيسية)
    test1 = "2 يوم (1447-03-28 إلى 1447-03-29)"
    result1 = pdf.safe_arabic_mixed(test1)
    print(f"📝 المدخل:  {test1}")
    print(f"✅ المخرج: {result1}\n")
    
    # اختبار 2: رقم الهوية مع الشرطة المائلة
    test2 = "رقم الهوية / الإقامة"
    result2 = pdf.safe_arabic_mixed(test2)
    print(f"📝 المدخل:  {test2}")
    print(f"✅ المخرج: {result2}\n")
    
    # اختبار 3: نص مختلط مع رموز متعددة
    test3 = "التقرير رقم (123/أ) صادر بتاريخ 2025-01-15"
    result3 = pdf.safe_arabic_mixed(test3)
    print(f"📝 المدخل:  {test3}")
    print(f"✅ المخرج: {result3}\n")
    
    # اختبار 4: توليد تقرير تجريبي
    print("🧪 جاري إنشاء تقرير تجريبي...\n")
    test_data = {
        'patient_name_ar': 'أحمد محمد السعيد',
        'patient_name_en': 'AHMED Mohammed Alsaeed',
        'id_number': '1122923749',
        'nationality_ar': 'سعودي',
        'nationality_en': 'Saudi Arabia',
        'employer_ar': 'طالب جامعي',
        'employer_en': 'University Student',
        'doctor_name_ar': 'نبيل حنا نصر حنا',
        'doctor_name_en': 'NABIL HANNA NASR HANNA',
        'position_ar': 'طبيب عام',
        'position_en': 'General',
        'admission_date_gregorian': '12-05-2025',
        'admission_date_hijri': '14-11-1446',
        'discharge_date_gregorian': '14-05-2025',
        'discharge_date_hijri': '16-11-1446',
        'issue_date_gregorian': '05-07-2025',
        'hospital_name_ar': 'مجمع عائلتي الطبي',
        'hospital_name_en': 'My Family Medical Center',
        'time': '6:23 AM'
    }
    try:
        pdf_path = generate_sick_leave_pdf(test_data, 'test')
        print(f"✅ تم إنشاء ملف PDF بنجاح: {pdf_path}")
        print(f"📌 افتح الملف وتأكد من ظهور: ")
        print(f"   • خلية المدة: 3 يوم (14-11-1446 إلى 16-11-1446)")
        print(f"   • خلية الهوية: رقم الهوية / الإقامة")
    except Exception as e:
        print(f"❌ خطأ أثناء إنشاء التقرير: {e}")
