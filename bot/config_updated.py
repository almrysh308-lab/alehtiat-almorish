# Configuration file for Seha Sick Leave Bot - Updated Version

import os

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '7853478744')

# API Settings - Same Railway website service
API_BASE_URL = os.environ.get('API_BASE_URL', 'https://alehtiat-almorish-production.up.railway.app')
API_ENDPOINT = '/api/bot/add_leave'
API_FULL_URL = API_BASE_URL + API_ENDPOINT
BOT_API_KEY = os.environ.get('BOT_API_KEY', 'seha_bot_secret_key_2025')

# Paths - Updated for current working directory
FONTS_DIR = '/app/fonts'
IMAGES_DIR = '/app'
OUTPUT_DIR = "/app/output"

# Font paths - Arabic
NOTO_SANS_ARABIC_BOLD = f'{FONTS_DIR}/noto_sans_arabic/NotoSansArabic-Bold.ttf'
NOTO_SANS_ARABIC_REGULAR = f'{FONTS_DIR}/noto_sans_arabic/NotoSansArabic-Regular.ttf'
# English: using built-in Times font (Times-Bold / Times-Roman)
# No custom font files needed for English text

# Image paths
SEHA_LOGO = f'{IMAGES_DIR}/شعارصحةseha.jpg'
GEOMETRIC_SHAPE = f'{IMAGES_DIR}/الشكلالهندسي.jpg'
KINGDOM_TEXT = f'{IMAGES_DIR}/كلمةالمملكةالعربيةالسعوديةKingdomofSaudiArabia.jpg'
HOSPITAL_LOGO = f'{IMAGES_DIR}/شعارالمستشفى.png'
HEALTH_INFO_CENTER_LOGO = f'{IMAGES_DIR}/شعارالمركزالوطنيللمعلوماتالصحية.jpg'

# QR Code settings
QR_URL = 'https://alehtiat-almorish-production.up.railway.app'
QR_DISPLAY_URL = 'www.seha.sa/#/inquiries/slenquiry'

# PDF settings
PDF_WIDTH = 297  # mm
PDF_HEIGHT = 419  # mm
