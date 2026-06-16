#!/bin/bash

# سكريبت تشغيل بوت تيليجرام للإجازات المرضية
# Seha Sick Leave Bot Startup Script

echo "🚀 بدء تشغيل بوت صحة للإجازات المرضية..."
echo "🚀 Starting Seha Sick Leave Bot..."

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 غير مثبت. يرجى تثبيت Python3 أولاً."
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

# التحقق من وجود pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 غير مثبت. يرجى تثبيت pip3 أولاً."
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# الانتقال إلى مجلد البوت
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 مجلد العمل: $SCRIPT_DIR"
echo "📁 Working directory: $SCRIPT_DIR"

# إنشاء البيئة الافتراضية إذا لم تكن موجودة
if [ ! -d "venv" ]; then
    echo "🔧 إنشاء البيئة الافتراضية..."
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# تفعيل البيئة الافتراضية
echo "🔧 تفعيل البيئة الافتراضية..."
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
echo "📦 Installing requirements..."
pip install -r requirements.txt

# إنشاء المجلدات المطلوبة
echo "📁 إنشاء المجلدات المطلوبة..."
echo "📁 Creating required directories..."
mkdir -p /app/output

# التحقق من متغيرات البيئة المطلوبة
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ متغير البيئة TELEGRAM_BOT_TOKEN غير محدد!"
    echo "❌ TELEGRAM_BOT_TOKEN environment variable is not set!"
    echo "📝 قم بتعيينه: export TELEGRAM_BOT_TOKEN=your_token_here"
    echo "📝 Set it: export TELEGRAM_BOT_TOKEN=your_token_here"
    exit 1
fi

echo "✅ جميع الإعدادات جاهزة!"
echo "✅ All configurations are ready!"
echo ""
echo "🤖 تشغيل البوت..."
echo "🤖 Starting the bot..."
echo ""

# تشغيل البوت المحدث
python3 bot_updated.py

