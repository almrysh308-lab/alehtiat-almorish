#!/bin/bash

# Seha Sick Leave Bot Setup Script
# سكريبت إعداد بوت صحة للإجازات المرضية

echo "🔧 إعداد بوت صحة للإجازات المرضية..."
echo "🔧 Setting up Seha Sick Leave Bot..."

# التحقق من وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python غير مثبت. يرجى تثبيت Python 3.9 أو أحدث"
    echo "❌ Python is not installed. Please install Python 3.9 or newer"
    exit 1
fi

echo "✅ تم العثور على Python"
echo "✅ Python found"

# إنشاء البيئة الافتراضية
if [ ! -d "bot_env" ]; then
    echo "📦 إنشاء البيئة الافتراضية..."
    echo "📦 Creating virtual environment..."
    python3 -m venv bot_env
    
    if [ $? -eq 0 ]; then
        echo "✅ تم إنشاء البيئة الافتراضية بنجاح"
        echo "✅ Virtual environment created successfully"
    else
        echo "❌ فشل في إنشاء البيئة الافتراضية"
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
else
    echo "✅ البيئة الافتراضية موجودة بالفعل"
    echo "✅ Virtual environment already exists"
fi

# تفعيل البيئة الافتراضية
echo "🔄 تفعيل البيئة الافتراضية..."
echo "🔄 Activating virtual environment..."
source bot_env/bin/activate

# تحديث pip
echo "⬆️ تحديث pip..."
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# تثبيت المكتبات المطلوبة
echo "📚 تثبيت المكتبات المطلوبة..."
echo "📚 Installing required packages..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ تم تثبيت جميع المكتبات بنجاح"
    echo "✅ All packages installed successfully"
else
    echo "❌ فشل في تثبيت بعض المكتبات"
    echo "❌ Failed to install some packages"
    exit 1
fi

# إنشاء المجلدات المطلوبة
echo "📁 إنشاء المجلدات المطلوبة..."
echo "📁 Creating required directories..."
mkdir -p output
mkdir -p output/logos

# جعل ملفات التشغيل قابلة للتنفيذ
echo "🔧 إعداد أذونات الملفات..."
echo "🔧 Setting file permissions..."
chmod +x start_bot.sh
chmod +x setup.sh

echo ""
echo "🎉 تم إعداد المشروع بنجاح!"
echo "🎉 Project setup completed successfully!"
echo ""
echo "📝 الخطوات التالية:"
echo "📝 Next steps:"
echo "1. تعيين متغير البيئة TELEGRAM_BOT_TOKEN"
echo "1. Set TELEGRAM_BOT_TOKEN environment variable"
echo "   export TELEGRAM_BOT_TOKEN=your_bot_token_here"
echo "2. تشغيل البوت باستخدام: ./start_bot.sh"
echo "2. Start the bot using: ./start_bot.sh"
echo ""

