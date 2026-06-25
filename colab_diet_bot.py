#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
DIET ASSISTANT TELEGRAM BOT - GOOGLE COLAB VERSION
=============================================================================
Multi-language (Uzbek, Russian, English) with Gemini AI Integration

USAGE IN GOOGLE COLAB:
1. Create a new Colab notebook
2. In the first cell, run: !pip install pyTelegramBotAPI google-generativeai pillow
3. Copy and paste this entire code into a new cell
4. Run the cell to start the bot

Author: Diet Bot Developer
Version: 1.0.0
=============================================================================
"""

# ============================================================================
# CONFIGURATION - Supports both direct values and environment variables
# ============================================================================
import os

# Get your Telegram Bot Token from @BotFather
# For Render: Set TELEGRAM_BOT_TOKEN in environment variables
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

# Get your Gemini API Key from https://makersuite.google.com/app/apikey
# For Render: Set GEMINI_API_KEY in environment variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")

# Your Telegram User ID (get it from @userinfobot)
# For Render: Set ADMIN_ID in environment variables
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789"))

# ============================================================================
# IMPORTS
# ============================================================================
import telebot
from telebot import types
import sqlite3
import google.generativeai as genai
from datetime import datetime, timedelta
import threading
import time
import traceback
from io import BytesIO

# Pillow import - Python 3.14+ compatible
try:
    from PIL import Image
    # Check if Pillow is properly installed (avoid __version__ issues in Python 3.14+)
    try:
        from PIL import __version__ as PIL_VERSION
        print(f"Pillow version: {PIL_VERSION}")
    except ImportError:
        # Fallback for newer Pillow versions
        import PIL
        PIL_VERSION = getattr(PIL, '__version__', 'unknown')
        print(f"Pillow loaded (version: {PIL_VERSION})")
except ImportError:
    print("Installing Pillow...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pillow>=10.4.0'])
    from PIL import Image

# ============================================================================
# INITIALIZE BOT AND GEMINI
# ============================================================================
print("Initializing bot...")
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=True)


print("Configuring Gemini AI...")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Thread lock for database operations
db_lock = threading.Lock()

# ============================================================================
# TRANSLATIONS - COMPREHENSIVE MULTI-LANGUAGE SUPPORT
# ============================================================================
TRANSLATIONS = {
    'uz': {
        'lang_name': "O'zbekcha",
        'welcome_lang': "Assalomu alaykum! Tilni tanlang:",
        'welcome': "Assalomu alaykum! Men sizning diyeta yordamchingizman. Tanishishni keling, yoshingizdan boshlasak - yoshingiz nechchida?",
        'ask_height': "Bo'yingiz uzunligini kiriting (masalan, 170 sm):",
        'ask_weight': "Vazningizni kiriting (masalan, 60 kg):",
        'ask_goal': "Maqsadingizni tanlang:",
        'ask_gender': "Jinsingizni tanlang:",
        'registration_complete': "Ro'yxatdan o'tganingiz bilan tabriklayman!\nBu botda siz o'z vazningizni oson nazorat qila olasiz\nSizga sovg'a sifatida 3 kunlik free trial taqdim qilamiz.",
        'main_menu': "Asosiy menyu:",
        'goal_lose': "Ozish",
        'goal_gain': "Vazn qo'shish",
        'goal_maintain': "Vaznni ushlab qolish",
        'gender_male': "Erkak",
        'gender_female': "Ayol",
        'vip_only': "Bu imkoniyatlar faqat VIP tarifda bo'ladi!",
        'daily_ration': "Kunlik ratsion",
        'daily_report': "1 kunlik hisobot",
        'weekly_report': "1 haftalik hisobot",
        'monthly_report': "1 oylik hisobot",
        'water_ration': "Suv ratsioni",
        'ai_chat': "AI Diyetolog Suhbat",
        'my_profile': "Profilim",
        'buy_vip': "VIP sotib olish",
        'about_me': "Men haqimda",
        'about_sub': "Obunam haqida",
        'edit_profile': "Men o'zgardim",
        'change_lang': "Tilni o'zgartirish",
        'back': "Orqaga",

        'i_drank': "Ichdim",
        'statistics': "Statistika",
        'i_will_eat': "Yeyman",
        'know_kcal': "Kkalni bilish",
        'make_vip': "VIP qilish",
        'vip_payment_info': "Karta raqami: 9860040114589092 N/N\nObuna narxi: 20 000 so'm.\nTo'lov qilgach, rasmni ovqat rasmi bilan adashtirmaslik uchun /chek buyrug'ini bosing yoki quyidagi tugmani bosing va chekni yuboring.",
        'send_receipt': "Chek yuborish",
        'receipt_received': "Chekingiz qabul qilindi! Admin tekshirgandan so'ng VIP statusingiz faollashtiriladi.",
        'vip_activated': "To'lovingiz tasdiqlandi! Siz endi VIP foydalanuvchisiz!",
        'profile_info': "Sizning profilingiz:\n\nYosh: {age} yosh\nBo'y: {height} sm\nVazn: {weight} kg\nMaqsad: {goal}\nJins: {gender}",
        'sub_info': "Obuna holati: {status}\nBoshlanish sanasi: {start}\nTugash sanasi: {end}\nQolgan kunlar: {days}",
        'sub_free': "Bepul (3 kunlik sinov)",
        'sub_vip': "VIP",
        'sub_expired': "Muddati tugagan",
        'water_recommendation': "Sizning ma'lumotlaringiz asosida kuniga {liters} litr suv ichishingiz kerak.",
        'water_logged': "Suv qo'shildi! Bugun jami: {total} ml ({glasses} stakan)",
        'water_stats': "Bugungi suv statistikasi:\n\nIchilgan: {total} ml\nMaqsad: {target} ml\nQoldi: {remaining} ml",
        'daily_report_text': "Bugungi hisobot:\n\nYeyilgan ovqatlar:\n{foods}\n\nJami kaloriya: {kcal} kcal\nOvqatlanish soni: {meals} marta",
        'weekly_report_text': "Haftalik hisobot:\n\nJami kaloriya: {kcal} kcal\nO'rtacha kunlik: {avg} kcal\nOvqatlanish soni: {meals} marta",
        'monthly_report_text': "Oylik hisobot:\n\nJami kaloriya: {kcal} kcal\nO'rtacha kunlik: {avg} kcal\nOvqatlanish soni: {meals} marta",
        'no_data': "Ma'lumot topilmadi",
        'ai_greeting': "Salom! Men AI diyetolog yordamchingizman. Ovqatlanish va parhez haqida savollaringizni bering.",
        'ai_off_topic': "Maqsadlar insonni yuksaltiradi, bizni maqsadimiz {goal}!",
        'daily_ration_text': "Sizning maqsadingiz: {goal}\n\nKunlik kaloriya maqsadi: {kcal} kcal\n\nTavsiya etilgan ovqatlar:\n{meals}",
        'breakfast': "Nonushta",
        'lunch': "Tushlik",
        'dinner': "Kechki ovqat",
        'snack': "Yengil tamaddi",
        'analyzing_food': "Ovqat tahlil qilinmoqda...",
        'edit_what': "Nimani o'zgartirmoqchisiz?",
        'edit_age': "Yoshni o'zgartirish",
        'edit_height': "Bo'yni o'zgartirish",
        'edit_weight': "Vaznni o'zgartirish",
        'edit_goal': "Maqsadni o'zgartirish",
        'edit_gender': "Jinsni o'zgartirish",
        'value_updated': "Ma'lumot yangilandi!",
        'food_logged': "Ovqat kunlik hisobotga qo'shildi!",
        'enter_new_age': "Yangi yoshingizni kiriting:",
        'enter_new_height': "Yangi bo'yingizni kiriting (sm):",
        'enter_new_weight': "Yangi vazningizni kiriting (kg):",
    },

    'ru': {
        'lang_name': "Русский",
        'welcome_lang': "Здравствуйте! Выберите язык:",
        'welcome': "Здравствуйте! Я ваш диетический помощник. Давайте познакомимся - сколько вам лет?",
        'ask_height': "Введите ваш рост (например, 170 см):",
        'ask_weight': "Введите ваш вес (например, 60 кг):",
        'ask_goal': "Выберите вашу цель:",
        'ask_gender': "Выберите ваш пол:",
        'registration_complete': "Поздравляю с регистрацией!\nВ этом боте вы можете легко контролировать свой вес\nВ подарок предоставляем 3-дневный бесплатный пробный период.",
        'main_menu': "Главное меню:",
        'goal_lose': "Похудеть",
        'goal_gain': "Набрать вес",
        'goal_maintain': "Поддерживать вес",
        'gender_male': "Мужчина",
        'gender_female': "Женщина",
        'vip_only': "Эта функция доступна только для VIP пользователей!",
        'daily_ration': "Дневной рацион",
        'daily_report': "Дневной отчет",
        'weekly_report': "Недельный отчет",
        'monthly_report': "Месячный отчет",
        'water_ration': "Водный режим",
        'ai_chat': "AI Диетолог Чат",
        'my_profile': "Мой профиль",
        'buy_vip': "Купить VIP",
        'about_me': "Обо мне",
        'about_sub': "О подписке",
        'edit_profile': "Изменить данные",
        'change_lang': "Сменить язык",
        'back': "Назад",
        'i_drank': "Выпил",
        'statistics': "Статистика",
        'i_will_eat': "Буду есть",
        'know_kcal': "Узнать ккал",
        'make_vip': "Сделать VIP",
        'vip_payment_info': "Номер карты: 9860040114589092 N/N\nЦена подписки: 20 000 сум.\nПосле оплаты нажмите /chek или кнопку ниже и отправьте чек.",
        'send_receipt': "Отправить чек",
        'receipt_received': "Ваш чек получен! После проверки админом ваш VIP статус будет активирован.",
        'vip_activated': "Ваш платеж подтвержден! Теперь вы VIP пользователь!",
        'profile_info': "Ваш профиль:\n\nВозраст: {age} лет\nРост: {height} см\nВес: {weight} кг\nЦель: {goal}\nПол: {gender}",
        'sub_info': "Статус подписки: {status}\nДата начала: {start}\nДата окончания: {end}\nОсталось дней: {days}",
        'sub_free': "Бесплатный (3-дневный пробный)",
        'sub_vip': "VIP",
        'sub_expired': "Истек",

        'water_recommendation': "На основе ваших данных вам нужно пить {liters} литров воды в день.",
        'water_logged': "Вода добавлена! Сегодня всего: {total} мл ({glasses} стаканов)",
        'water_stats': "Статистика воды за сегодня:\n\nВыпито: {total} мл\nЦель: {target} мл\nОсталось: {remaining} мл",
        'daily_report_text': "Сегодняшний отчет:\n\nСъеденные продукты:\n{foods}\n\nВсего калорий: {kcal} ккал\nКоличество приемов пищи: {meals}",
        'weekly_report_text': "Недельный отчет:\n\nВсего калорий: {kcal} ккал\nСреднее за день: {avg} ккал\nКоличество приемов пищи: {meals}",
        'monthly_report_text': "Месячный отчет:\n\nВсего калорий: {kcal} ккал\nСреднее за день: {avg} ккал\nКоличество приемов пищи: {meals}",
        'no_data': "Данные не найдены",
        'ai_greeting': "Привет! Я ваш AI диетолог помощник. Задавайте вопросы о питании и диете.",
        'ai_off_topic': "Цели возвышают человека, наша цель - {goal}!",
        'daily_ration_text': "Ваша цель: {goal}\n\nДневная норма калорий: {kcal} ккал\n\nРекомендуемые блюда:\n{meals}",
        'breakfast': "Завтрак",
        'lunch': "Обед",
        'dinner': "Ужин",
        'snack': "Перекус",
        'analyzing_food': "Анализируем еду...",
        'edit_what': "Что хотите изменить?",
        'edit_age': "Изменить возраст",
        'edit_height': "Изменить рост",
        'edit_weight': "Изменить вес",
        'edit_goal': "Изменить цель",
        'edit_gender': "Изменить пол",
        'value_updated': "Данные обновлены!",
        'food_logged': "Еда добавлена в дневной отчет!",
        'enter_new_age': "Введите ваш новый возраст:",
        'enter_new_height': "Введите ваш новый рост (см):",
        'enter_new_weight': "Введите ваш новый вес (кг):",
    },

    'en': {
        'lang_name': "English",
        'welcome_lang': "Hello! Choose your language:",
        'welcome': "Hello! I'm your diet assistant. Let's get to know each other - how old are you?",
        'ask_height': "Enter your height (e.g., 170 cm):",
        'ask_weight': "Enter your weight (e.g., 60 kg):",
        'ask_goal': "Choose your goal:",
        'ask_gender': "Choose your gender:",
        'registration_complete': "Congratulations on registration!\nIn this bot you can easily control your weight\nAs a gift, we provide a 3-day free trial.",
        'main_menu': "Main menu:",
        'goal_lose': "Lose weight",
        'goal_gain': "Gain weight",
        'goal_maintain': "Maintain weight",
        'gender_male': "Male",
        'gender_female': "Female",
        'vip_only': "This feature is only available for VIP users!",
        'daily_ration': "Daily ration",
        'daily_report': "Daily report",
        'weekly_report': "Weekly report",
        'monthly_report': "Monthly report",
        'water_ration': "Water regime",
        'ai_chat': "AI Dietitian Chat",
        'my_profile': "My Profile",
        'buy_vip': "Buy VIP",
        'about_me': "About me",
        'about_sub': "About subscription",
        'edit_profile': "Edit profile",
        'change_lang': "Change language",
        'back': "Back",
        'i_drank': "I drank",
        'statistics': "Statistics",
        'i_will_eat': "I'll eat",
        'know_kcal': "Know kcal",
        'make_vip': "Make VIP",
        'vip_payment_info': "Card number: 9860040114589092 N/N\nSubscription price: 20,000 sum.\nAfter payment, press /chek or the button below and send the receipt.",
        'send_receipt': "Send receipt",
        'receipt_received': "Your receipt has been received! Your VIP status will be activated after admin verification.",
        'vip_activated': "Your payment has been confirmed! You are now a VIP user!",
        'profile_info': "Your profile:\n\nAge: {age} years\nHeight: {height} cm\nWeight: {weight} kg\nGoal: {goal}\nGender: {gender}",
        'sub_info': "Subscription status: {status}\nStart date: {start}\nEnd date: {end}\nDays remaining: {days}",
        'sub_free': "Free (3-day trial)",
        'sub_vip': "VIP",
        'sub_expired': "Expired",

        'water_recommendation': "Based on your data, you need to drink {liters} liters of water per day.",
        'water_logged': "Water added! Today total: {total} ml ({glasses} glasses)",
        'water_stats': "Today's water statistics:\n\nDrank: {total} ml\nGoal: {target} ml\nRemaining: {remaining} ml",
        'daily_report_text': "Today's report:\n\nFoods eaten:\n{foods}\n\nTotal calories: {kcal} kcal\nNumber of meals: {meals}",
        'weekly_report_text': "Weekly report:\n\nTotal calories: {kcal} kcal\nDaily average: {avg} kcal\nNumber of meals: {meals}",
        'monthly_report_text': "Monthly report:\n\nTotal calories: {kcal} kcal\nDaily average: {avg} kcal\nNumber of meals: {meals}",
        'no_data': "No data found",
        'ai_greeting': "Hello! I'm your AI dietitian assistant. Ask me questions about nutrition and diet.",
        'ai_off_topic': "Goals elevate people, our goal is {goal}!",
        'daily_ration_text': "Your goal: {goal}\n\nDaily calorie target: {kcal} kcal\n\nRecommended meals:\n{meals}",
        'breakfast': "Breakfast",
        'lunch': "Lunch",
        'dinner': "Dinner",
        'snack': "Snack",
        'analyzing_food': "Analyzing food...",
        'edit_what': "What would you like to change?",
        'edit_age': "Change age",
        'edit_height': "Change height",
        'edit_weight': "Change weight",
        'edit_goal': "Change goal",
        'edit_gender': "Change gender",
        'value_updated': "Data updated!",
        'food_logged': "Food added to daily report!",
        'enter_new_age': "Enter your new age:",
        'enter_new_height': "Enter your new height (cm):",
        'enter_new_weight': "Enter your new weight (kg):",
    }
}

def get_text(user_id, key):
    """Get translated text for user's language"""
    lang = get_user_language(user_id)
    return TRANSLATIONS.get(lang, TRANSLATIONS['uz']).get(key, TRANSLATIONS['uz'].get(key, key))

def get_goal_text(user_id, goal_key):
    """Get translated goal text"""
    lang = get_user_language(user_id)
    goal_map = {'lose': 'goal_lose', 'gain': 'goal_gain', 'maintain': 'goal_maintain'}
    return TRANSLATIONS.get(lang, TRANSLATIONS['uz']).get(goal_map.get(goal_key, 'goal_maintain'), goal_key)


# ============================================================================
# DATABASE SETUP AND OPERATIONS
# ============================================================================
def init_database():
    """Initialize SQLite database with all required tables"""
    with db_lock:
        conn = sqlite3.connect('diet_bot.db', check_same_thread=False)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                language TEXT DEFAULT 'uz',
                age INTEGER,
                height REAL,
                weight REAL,
                goal TEXT,
                gender TEXT,
                state TEXT DEFAULT 'new',
                subscription_status TEXT DEFAULT 'free',
                subscription_start TIMESTAMP,
                subscription_end TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                food_name TEXT,
                calories REAL,
                portion TEXT,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount_ml INTEGER DEFAULT 250,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully!")

def get_db_connection():
    return sqlite3.connect('diet_bot.db', check_same_thread=False)


def get_user(user_id):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

def create_user(user_id, username):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id, username, state) VALUES (?, ?, ?)', 
                      (user_id, username, 'select_language'))
        conn.commit()
        conn.close()

def update_user_state(user_id, state):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET state = ? WHERE user_id = ?', (state, user_id))
        conn.commit()
        conn.close()

def update_user_field(user_id, field, value):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f'UPDATE users SET {field} = ? WHERE user_id = ?', (value, user_id))
        conn.commit()
        conn.close()

def get_user_state(user_id):
    user = get_user(user_id)
    return user[8] if user else None

def get_user_language(user_id):
    user = get_user(user_id)
    return user[2] if user else 'uz'

def is_user_vip(user_id):
    user = get_user(user_id)
    if not user:
        return False
    sub_status = user[9]
    sub_end = user[11]
    if sub_status == 'vip' and sub_end:
        try:
            end_date = datetime.strptime(sub_end, '%Y-%m-%d %H:%M:%S')
            return end_date > datetime.now()
        except:
            return False
    if sub_status == 'free':
        created = user[12]
        if created:
            try:
                created_date = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
                return (datetime.now() - created_date).days < 3
            except:
                return True
    return False


def is_in_free_trial(user_id):
    user = get_user(user_id)
    if not user:
        return False
    sub_status = user[9]
    if sub_status != 'free':
        return False
    created = user[12]
    if created:
        try:
            created_date = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
            return (datetime.now() - created_date).days < 3
        except:
            return True
    return True

def activate_vip(user_id):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        cursor.execute('''
            UPDATE users SET subscription_status = 'vip', subscription_start = ?, subscription_end = ?
            WHERE user_id = ?
        ''', (start_date.strftime('%Y-%m-%d %H:%M:%S'), end_date.strftime('%Y-%m-%d %H:%M:%S'), user_id))
        conn.commit()
        conn.close()

def get_all_users():
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()
        return users

def log_food(user_id, food_name, calories, portion=""):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO food_logs (user_id, food_name, calories, portion) VALUES (?, ?, ?, ?)',
                      (user_id, food_name, calories, portion))
        conn.commit()
        conn.close()

def log_water(user_id, amount_ml=250):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO water_logs (user_id, amount_ml) VALUES (?, ?)', (user_id, amount_ml))
        conn.commit()
        conn.close()


def get_daily_food_logs(user_id):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT food_name, calories, portion FROM food_logs WHERE user_id = ? AND date(logged_at) = ?',
                      (user_id, today))
        logs = cursor.fetchall()
        conn.close()
        return logs

def get_weekly_food_logs(user_id):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute('SELECT food_name, calories FROM food_logs WHERE user_id = ? AND date(logged_at) >= ?',
                      (user_id, week_ago))
        logs = cursor.fetchall()
        conn.close()
        return logs

def get_monthly_food_logs(user_id):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        cursor.execute('SELECT food_name, calories FROM food_logs WHERE user_id = ? AND date(logged_at) >= ?',
                      (user_id, month_ago))
        logs = cursor.fetchall()
        conn.close()
        return logs

def get_daily_water(user_id):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('SELECT SUM(amount_ml) FROM water_logs WHERE user_id = ? AND date(logged_at) = ?',
                      (user_id, today))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result[0] else 0


# ============================================================================
# CALORIE AND WATER CALCULATIONS
# ============================================================================
def calculate_daily_calories(user_id):
    user = get_user(user_id)
    if not user:
        return 2000
    age = user[3] or 30
    height = user[4] or 170
    weight = user[5] or 70
    goal = user[6] or 'maintain'
    gender = user[7] or 'male'
    
    if gender == 'male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    tdee = bmr * 1.55
    if goal == 'lose':
        return int(tdee - 500)
    elif goal == 'gain':
        return int(tdee + 500)
    return int(tdee)

def calculate_water_recommendation(user_id):
    user = get_user(user_id)
    if not user:
        return 2.0
    weight = user[5] or 70
    return round(weight * 0.033, 1)

# ============================================================================
# KEYBOARD BUILDERS
# ============================================================================
def get_language_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("English", callback_data="lang_en")
    )
    return keyboard

def get_goal_keyboard(user_id):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(f"{t['goal_lose']}"))
    keyboard.add(types.KeyboardButton(f"{t['goal_gain']}"))
    keyboard.add(types.KeyboardButton(f"{t['goal_maintain']}"))
    return keyboard

def get_gender_keyboard(user_id):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton(f"{t['gender_male']}"), types.KeyboardButton(f"{t['gender_female']}"))
    return keyboard


def get_main_menu_keyboard(user_id):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(f"{t['daily_ration']}"), types.KeyboardButton(f"{t['daily_report']}"))
    keyboard.add(types.KeyboardButton(f"{t['weekly_report']}"), types.KeyboardButton(f"{t['monthly_report']}"))
    keyboard.add(types.KeyboardButton(f"{t['water_ration']}"), types.KeyboardButton(f"{t['ai_chat']}"))
    keyboard.add(types.KeyboardButton(f"{t['my_profile']}"), types.KeyboardButton(f"{t['buy_vip']}"))
    return keyboard

def get_profile_keyboard(user_id):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(f"{t['about_me']}"), types.KeyboardButton(f"{t['about_sub']}"))
    keyboard.add(types.KeyboardButton(f"{t['edit_profile']}"), types.KeyboardButton(f"{t['change_lang']}"))
    keyboard.add(types.KeyboardButton(f"{t['back']}"))
    return keyboard

def get_edit_profile_keyboard(user_id):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(f"{t['edit_age']}"), types.KeyboardButton(f"{t['edit_height']}"))
    keyboard.add(types.KeyboardButton(f"{t['edit_weight']}"), types.KeyboardButton(f"{t['edit_goal']}"))
    keyboard.add(types.KeyboardButton(f"{t['edit_gender']}"), types.KeyboardButton(f"{t['back']}"))
    return keyboard

def get_water_keyboard(user_id):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(f"{t['i_drank']}", callback_data="water_drink"),
        types.InlineKeyboardButton(f"{t['statistics']}", callback_data="water_stats")
    )
    return keyboard

def get_food_analysis_keyboard(user_id, food_info=""):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(f"{t['i_will_eat']}", callback_data=f"food_log:{food_info[:30]}"),
        types.InlineKeyboardButton(f"{t['know_kcal']}", callback_data="food_kcal")
    )
    return keyboard


def get_vip_keyboard(user_id):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(f"{t['send_receipt']}", callback_data="send_receipt"))
    return keyboard

def get_admin_vip_keyboard(target_user_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("VIP qilish", callback_data=f"admin_vip:{target_user_id}"))
    return keyboard

def get_back_keyboard(user_id):
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(f"{t['back']}"))
    return keyboard

# ============================================================================
# GEMINI AI FUNCTIONS
# ============================================================================
def analyze_food_with_gemini(image, user_id):
    lang = get_user_language(user_id)
    lang_instructions = {
        'uz': "O'zbek tilida javob bering.",
        'ru': "Ответьте на русском языке.",
        'en': "Respond in English."
    }
    
    prompt = f"""You are a professional nutritionist analyzing food.
{lang_instructions.get(lang, lang_instructions['uz'])}

Analyze this food image and provide:
1. Name of the dish/food
2. Estimated portion size (be specific and realistic based on visual - avoid generic numbers like always 200g)
3. Estimated weight in grams (analyze visual cues: plate size, utensils, food density)
4. Calorie content (kcal)
5. Macronutrients (protein, carbs, fat in grams)
6. Brief nutritional advice

Be realistic with portion estimates. Consider the visual context carefully."""

    try:
        response = gemini_model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_food_text_with_gemini(food_text, user_id):
    lang = get_user_language(user_id)
    lang_instructions = {
        'uz': "O'zbek tilida javob bering.",
        'ru': "Ответьте на русском языке.",
        'en': "Respond in English."
    }
    
    prompt = f"""You are a professional nutritionist.
{lang_instructions.get(lang, lang_instructions['uz'])}

The user mentioned this food: "{food_text}"

Provide:
1. Name of the dish/food
2. Typical portion size
3. Estimated weight in grams
4. Calorie content (kcal) for a typical portion
5. Macronutrients (protein, carbs, fat in grams)
6. Brief nutritional advice"""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def get_ai_diet_response(user_message, user_id):
    user = get_user(user_id)
    goal = user[6] if user else 'maintain'
    lang = get_user_language(user_id)
    
    lang_instructions = {
        'uz': "O'zbek tilida javob bering.",
        'ru': "Ответьте на русском языке.",
        'en': "Respond in English."
    }
    
    goal_text = get_goal_text(user_id, goal)
    off_topic_response = get_text(user_id, 'ai_off_topic').format(goal=goal_text)
    
    prompt = f"""You are a professional nutritionist and dietitian assistant.
{lang_instructions.get(lang, lang_instructions['uz'])}

User's goal: {goal_text}

IMPORTANT RULES:
1. Only answer questions related to nutrition, diet, food, health, weight management, and fitness.
2. If the user asks about anything unrelated, respond with EXACTLY: "{off_topic_response}"
3. Keep responses helpful, professional, and focused on their goal.

User message: {user_message}"""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


def get_daily_meal_recommendations(user_id):
    user = get_user(user_id)
    if not user:
        return "User data not found"
    
    goal = user[6] or 'maintain'
    weight = user[5] or 70
    calories = calculate_daily_calories(user_id)
    lang = get_user_language(user_id)
    
    lang_instructions = {
        'uz': "O'zbek tilida javob bering. O'zbekiston oshxonasiga mos ovqatlarni tavsiya qiling.",
        'ru': "Ответьте на русском языке. Рекомендуйте блюда, подходящие для узбекской кухни.",
        'en': "Respond in English. Recommend dishes suitable for Uzbek cuisine."
    }
    
    goal_text = get_goal_text(user_id, goal)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    
    prompt = f"""You are a professional nutritionist.
{lang_instructions.get(lang, lang_instructions['uz'])}

Create a daily meal plan for:
- Weight: {weight} kg
- Goal: {goal_text}
- Daily calorie target: {calories} kcal

Provide specific meals:
1. {t['breakfast']} (with calories)
2. {t['snack']} (with calories)
3. {t['lunch']} (with calories)
4. {t['snack']} (with calories)
5. {t['dinner']} (with calories)

Include portion sizes and keep total within calorie target."""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# COMMAND HANDLERS
# ============================================================================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    create_user(user_id, username)
    update_user_state(user_id, 'select_language')
    
    bot.send_message(
        user_id,
        "Assalomu alaykum! Tilni tanlang:\nЗдравствуйте! Выберите язык:\nHello! Choose your language:",
        reply_markup=get_language_keyboard()
    )

@bot.message_handler(commands=['chek'])
def chek_command(message):
    user_id = message.from_user.id
    update_user_state(user_id, 'waiting_receipt')
    lang = get_user_language(user_id)
    receipt_msg = {
        'uz': "Iltimos, to'lov chekingizni rasm sifatida yuboring:",
        'ru': "Пожалуйста, отправьте фото вашего чека об оплате:",
        'en': "Please send your payment receipt as an image:"
    }
    bot.send_message(user_id, receipt_msg.get(lang, receipt_msg['uz']), reply_markup=get_back_keyboard(user_id))

@bot.message_handler(commands=['user'])
def user_stats_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    users = get_all_users()
    total = len(users)
    vip_users = [u for u in users if u[9] == 'vip']
    free_users = [u for u in users if u[9] != 'vip']
    
    vip_list = "\n".join([f"@{u[1]}" for u in vip_users if u[1]]) if vip_users else "Yo'q"
    free_list = "\n".join([f"@{u[1]}" for u in free_users[:20] if u[1]]) if free_users else "Yo'q"
    
    stats_text = f"""Bot statistikasi:

Jami foydalanuvchilar: {total}

VIP foydalanuvchilar: {len(vip_users)}
{vip_list}

Bepul foydalanuvchilar: {len(free_users)}
{free_list}{"..." if len(free_users) > 20 else ""}"""
    
    bot.send_message(ADMIN_ID, stats_text)

@bot.message_handler(commands=['reklama'])
def reklama_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    update_user_state(ADMIN_ID, 'waiting_broadcast')
    bot.send_message(ADMIN_ID, "Reklama xabarini yuboring (matn yoki rasm+izoh):")


# ============================================================================
# CALLBACK QUERY HANDLERS
# ============================================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def language_selection_callback(call):
    user_id = call.from_user.id
    lang = call.data.split('_')[1]
    update_user_field(user_id, 'language', lang)
    update_user_state(user_id, 'waiting_age')
    bot.answer_callback_query(call.id)
    bot.edit_message_text(get_text(user_id, 'welcome'), chat_id=user_id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'water_drink')
def water_drink_callback(call):
    user_id = call.from_user.id
    if not is_user_vip(user_id) and not is_in_free_trial(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, 'vip_only'), show_alert=True)
        return
    log_water(user_id, 250)
    total = get_daily_water(user_id)
    glasses = total // 250
    bot.answer_callback_query(call.id, get_text(user_id, 'water_logged').format(total=total, glasses=glasses))

@bot.callback_query_handler(func=lambda call: call.data == 'water_stats')
def water_stats_callback(call):
    user_id = call.from_user.id
    if not is_user_vip(user_id) and not is_in_free_trial(user_id):
        bot.answer_callback_query(call.id, get_text(user_id, 'vip_only'), show_alert=True)
        return
    total = get_daily_water(user_id)
    target = int(calculate_water_recommendation(user_id) * 1000)
    remaining = max(0, target - total)
    stats_text = get_text(user_id, 'water_stats').format(total=total, target=target, remaining=remaining)
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, stats_text)

@bot.callback_query_handler(func=lambda call: call.data.startswith('food_log:'))
def food_log_callback(call):
    user_id = call.from_user.id
    food_info = call.data.replace('food_log:', '')
    log_food(user_id, food_info or "Analyzed food", 300, "1 portion")
    bot.answer_callback_query(call.id, get_text(user_id, 'food_logged'))

@bot.callback_query_handler(func=lambda call: call.data == 'food_kcal')
def food_kcal_callback(call):
    bot.answer_callback_query(call.id, "Kaloriya yuqoridagi tahlilda / Calories shown above")

@bot.callback_query_handler(func=lambda call: call.data == 'send_receipt')
def send_receipt_callback(call):
    user_id = call.from_user.id
    update_user_state(user_id, 'waiting_receipt')
    lang = get_user_language(user_id)
    receipt_msg = {
        'uz': "Iltimos, to'lov chekingizni rasm sifatida yuboring:",
        'ru': "Пожалуйста, отправьте фото вашего чека:",
        'en': "Please send your payment receipt as an image:"
    }
    bot.answer_callback_query(call.id)
    bot.send_message(user_id, receipt_msg.get(lang, receipt_msg['uz']), reply_markup=get_back_keyboard(user_id))


@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_vip:'))
def admin_vip_callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Ruxsat yo'q!")
        return
    target_user_id = int(call.data.split(':')[1])
    activate_vip(target_user_id)
    user_lang = get_user_language(target_user_id)
    vip_msg = TRANSLATIONS.get(user_lang, TRANSLATIONS['uz'])['vip_activated']
    try:
        bot.send_message(target_user_id, f"{vip_msg}", reply_markup=get_main_menu_keyboard(target_user_id))
    except:
        pass
    bot.answer_callback_query(call.id, "VIP faollashtirildi!")
    bot.edit_message_text(f"VIP faollashtirildi: {target_user_id}", chat_id=ADMIN_ID, message_id=call.message.message_id)

# ============================================================================
# PHOTO HANDLER - FOOD ANALYSIS
# ============================================================================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    state = get_user_state(user_id)
    
    # Receipt handling
    if state == 'waiting_receipt':
        try:
            user = get_user(user_id)
            username = user[1] if user else str(user_id)
            bot.forward_message(ADMIN_ID, user_id, message.message_id)
            bot.send_message(ADMIN_ID, f"To'lov cheki:\nUser ID: {user_id}\nUsername: @{username}",
                           reply_markup=get_admin_vip_keyboard(user_id))
            bot.send_message(user_id, get_text(user_id, 'receipt_received'),
                           reply_markup=get_main_menu_keyboard(user_id))
            update_user_state(user_id, 'main_menu')
        except Exception as e:
            print(f"Error forwarding receipt: {e}")
        return
    
    # Admin broadcast with image
    if user_id == ADMIN_ID and state == 'waiting_broadcast':
        users = get_all_users()
        sent = 0
        caption = message.caption or ""
        for user in users:
            try:
                bot.send_photo(user[0], message.photo[-1].file_id, caption=caption)
                sent += 1
            except:
                pass
        bot.send_message(ADMIN_ID, f"Rasm {sent}/{len(users)} foydalanuvchiga yuborildi.")
        update_user_state(ADMIN_ID, 'main_menu')
        return
    
    # Food photo analysis - available to ALL users
    bot.send_message(user_id, get_text(user_id, 'analyzing_food'))
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = Image.open(BytesIO(downloaded_file))
        analysis = analyze_food_with_gemini(image, user_id)
        bot.send_message(user_id, analysis, reply_markup=get_food_analysis_keyboard(user_id, "food"))
    except Exception as e:
        bot.send_message(user_id, f"Xatolik: {str(e)}")


# ============================================================================
# TEXT MESSAGE HANDLER
# ============================================================================
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    state = get_user_state(user_id)
    lang = get_user_language(user_id)
    t = TRANSLATIONS.get(lang, TRANSLATIONS['uz'])
    
    # Admin broadcast handling
    if user_id == ADMIN_ID and state == 'waiting_broadcast':
        users = get_all_users()
        sent = 0
        for user in users:
            try:
                bot.send_message(user[0], text)
                sent += 1
            except:
                pass
        bot.send_message(ADMIN_ID, f"Xabar {sent}/{len(users)} foydalanuvchiga yuborildi.")
        update_user_state(ADMIN_ID, 'main_menu')
        return
    
    # Registration flow - Age
    if state == 'waiting_age':
        try:
            age = int(''.join(filter(str.isdigit, text)))
            if 7 <= age <= 80:
                update_user_field(user_id, 'age', age)
                update_user_state(user_id, 'waiting_height')
                bot.send_message(user_id, get_text(user_id, 'ask_height'))
        except:
            pass
        return
    
    # Registration flow - Height
    if state == 'waiting_height':
        try:
            height = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
            if 50 <= height <= 250:
                update_user_field(user_id, 'height', height)
                update_user_state(user_id, 'waiting_weight')
                bot.send_message(user_id, get_text(user_id, 'ask_weight'))
        except:
            pass
        return
    
    # Registration flow - Weight
    if state == 'waiting_weight':
        try:
            weight = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
            if 20 <= weight <= 300:
                update_user_field(user_id, 'weight', weight)
                update_user_state(user_id, 'waiting_goal')
                bot.send_message(user_id, get_text(user_id, 'ask_goal'), reply_markup=get_goal_keyboard(user_id))
        except:
            pass
        return

    
    # Registration flow - Goal
    if state == 'waiting_goal':
        goal_map = {t['goal_lose']: 'lose', t['goal_gain']: 'gain', t['goal_maintain']: 'maintain'}
        goal = goal_map.get(text)
        if goal:
            update_user_field(user_id, 'goal', goal)
            update_user_state(user_id, 'waiting_gender')
            bot.send_message(user_id, get_text(user_id, 'ask_gender'), reply_markup=get_gender_keyboard(user_id))
        return
    
    # Registration flow - Gender
    if state == 'waiting_gender':
        gender_map = {t['gender_male']: 'male', t['gender_female']: 'female'}
        gender = gender_map.get(text)
        if gender:
            update_user_field(user_id, 'gender', gender)
            update_user_state(user_id, 'main_menu')
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            update_user_field(user_id, 'subscription_start', now)
            trial_end = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
            update_user_field(user_id, 'subscription_end', trial_end)
            bot.send_message(user_id, get_text(user_id, 'registration_complete'), reply_markup=get_main_menu_keyboard(user_id))
        return
    
    # Edit profile states
    if state == 'edit_age':
        try:
            age = int(''.join(filter(str.isdigit, text)))
            if 7 <= age <= 80:
                update_user_field(user_id, 'age', age)
                update_user_state(user_id, 'main_menu')
                bot.send_message(user_id, get_text(user_id, 'value_updated'), reply_markup=get_main_menu_keyboard(user_id))
        except:
            pass
        return
    
    if state == 'edit_height':
        try:
            height = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
            if 50 <= height <= 250:
                update_user_field(user_id, 'height', height)
                update_user_state(user_id, 'main_menu')
                bot.send_message(user_id, get_text(user_id, 'value_updated'), reply_markup=get_main_menu_keyboard(user_id))
        except:
            pass
        return
    
    if state == 'edit_weight':
        try:
            weight = float(''.join(filter(lambda x: x.isdigit() or x == '.', text)))
            if 20 <= weight <= 300:
                update_user_field(user_id, 'weight', weight)
                update_user_state(user_id, 'main_menu')
                bot.send_message(user_id, get_text(user_id, 'value_updated'), reply_markup=get_main_menu_keyboard(user_id))
        except:
            pass
        return

    
    if state == 'edit_goal':
        goal_map = {t['goal_lose']: 'lose', t['goal_gain']: 'gain', t['goal_maintain']: 'maintain'}
        goal = goal_map.get(text)
        if goal:
            update_user_field(user_id, 'goal', goal)
            update_user_state(user_id, 'main_menu')
            bot.send_message(user_id, get_text(user_id, 'value_updated'), reply_markup=get_main_menu_keyboard(user_id))
        return
    
    if state == 'edit_gender':
        gender_map = {t['gender_male']: 'male', t['gender_female']: 'female'}
        gender = gender_map.get(text)
        if gender:
            update_user_field(user_id, 'gender', gender)
            update_user_state(user_id, 'main_menu')
            bot.send_message(user_id, get_text(user_id, 'value_updated'), reply_markup=get_main_menu_keyboard(user_id))
        return
    
    # AI Chat mode
    if state == 'ai_chat':
        if text == t['back']:
            update_user_state(user_id, 'main_menu')
            bot.send_message(user_id, get_text(user_id, 'main_menu'), reply_markup=get_main_menu_keyboard(user_id))
            return
        response = get_ai_diet_response(text, user_id)
        bot.send_message(user_id, response, reply_markup=get_back_keyboard(user_id))
        return
    
    # ==================== MAIN MENU HANDLING ====================
    
    # Back button
    if text == t['back']:
        update_user_state(user_id, 'main_menu')
        bot.send_message(user_id, get_text(user_id, 'main_menu'), reply_markup=get_main_menu_keyboard(user_id))
        return
    
    # Daily Ration
    if text == t['daily_ration']:
        if not is_user_vip(user_id) and not is_in_free_trial(user_id):
            bot.send_message(user_id, get_text(user_id, 'vip_only'))
            return
        bot.send_message(user_id, get_text(user_id, 'analyzing_food'))
        recommendations = get_daily_meal_recommendations(user_id)
        calories = calculate_daily_calories(user_id)
        user = get_user(user_id)
        goal_text = get_goal_text(user_id, user[6] if user else 'maintain')
        response = get_text(user_id, 'daily_ration_text').format(goal=goal_text, kcal=calories, meals=recommendations)
        bot.send_message(user_id, response)
        return

    
    # Daily Report
    if text == t['daily_report']:
        if not is_user_vip(user_id) and not is_in_free_trial(user_id):
            bot.send_message(user_id, get_text(user_id, 'vip_only'))
            return
        logs = get_daily_food_logs(user_id)
        if not logs:
            bot.send_message(user_id, get_text(user_id, 'no_data'))
            return
        foods = "\n".join([f"- {log[0]} ({log[1]} kcal)" for log in logs])
        total_kcal = sum([log[1] for log in logs])
        meals = len(logs)
        report = get_text(user_id, 'daily_report_text').format(foods=foods, kcal=int(total_kcal), meals=meals)
        bot.send_message(user_id, report)
        return
    
    # Weekly Report
    if text == t['weekly_report']:
        if not is_user_vip(user_id) and not is_in_free_trial(user_id):
            bot.send_message(user_id, get_text(user_id, 'vip_only'))
            return
        logs = get_weekly_food_logs(user_id)
        if not logs:
            bot.send_message(user_id, get_text(user_id, 'no_data'))
            return
        total_kcal = sum([log[1] for log in logs])
        meals = len(logs)
        avg = int(total_kcal / 7) if total_kcal > 0 else 0
        report = get_text(user_id, 'weekly_report_text').format(kcal=int(total_kcal), avg=avg, meals=meals)
        bot.send_message(user_id, report)
        return
    
    # Monthly Report
    if text == t['monthly_report']:
        if not is_user_vip(user_id) and not is_in_free_trial(user_id):
            bot.send_message(user_id, get_text(user_id, 'vip_only'))
            return
        logs = get_monthly_food_logs(user_id)
        if not logs:
            bot.send_message(user_id, get_text(user_id, 'no_data'))
            return
        total_kcal = sum([log[1] for log in logs])
        meals = len(logs)
        avg = int(total_kcal / 30) if total_kcal > 0 else 0
        report = get_text(user_id, 'monthly_report_text').format(kcal=int(total_kcal), avg=avg, meals=meals)
        bot.send_message(user_id, report)
        return

    
    # Water Ration
    if text == t['water_ration']:
        if not is_user_vip(user_id) and not is_in_free_trial(user_id):
            bot.send_message(user_id, get_text(user_id, 'vip_only'))
            return
        liters = calculate_water_recommendation(user_id)
        recommendation = get_text(user_id, 'water_recommendation').format(liters=liters)
        bot.send_message(user_id, recommendation, reply_markup=get_water_keyboard(user_id))
        return
    
    # AI Dietitian Chat
    if text == t['ai_chat']:
        if not is_user_vip(user_id) and not is_in_free_trial(user_id):
            bot.send_message(user_id, get_text(user_id, 'vip_only'))
            return
        update_user_state(user_id, 'ai_chat')
        bot.send_message(user_id, get_text(user_id, 'ai_greeting'), reply_markup=get_back_keyboard(user_id))
        return
    
    # My Profile
    if text == t['my_profile']:
        update_user_state(user_id, 'profile_menu')
        bot.send_message(user_id, get_text(user_id, 'my_profile'), reply_markup=get_profile_keyboard(user_id))
        return
    
    # Buy VIP
    if text == t['buy_vip']:
        bot.send_message(user_id, get_text(user_id, 'vip_payment_info'), reply_markup=get_vip_keyboard(user_id))
        return
    
    # ==================== PROFILE SUBMENU ====================
    
    # About Me
    if text == t['about_me']:
        user = get_user(user_id)
        if user:
            goal_text = get_goal_text(user_id, user[6])
            gender_text = t['gender_male'] if user[7] == 'male' else t['gender_female']
            profile = get_text(user_id, 'profile_info').format(
                age=user[3] or '-', height=user[4] or '-', weight=user[5] or '-',
                goal=goal_text, gender=gender_text
            )
            bot.send_message(user_id, profile)
        return

    
    # About Subscription
    if text == t['about_sub']:
        user = get_user(user_id)
        if user:
            sub_status = user[9]
            start = user[10] or '-'
            end = user[11] or '-'
            
            if sub_status == 'vip':
                status_text = t['sub_vip']
                if end != '-':
                    try:
                        end_date = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                        days_left = (end_date - datetime.now()).days
                    except:
                        days_left = 0
                else:
                    days_left = 0
            elif is_in_free_trial(user_id):
                status_text = t['sub_free']
                created = user[12]
                if created:
                    try:
                        created_date = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
                        days_left = 3 - (datetime.now() - created_date).days
                    except:
                        days_left = 0
                else:
                    days_left = 0
            else:
                status_text = t['sub_expired']
                days_left = 0
            
            sub_info = get_text(user_id, 'sub_info').format(
                status=status_text,
                start=start[:10] if start != '-' else '-',
                end=end[:10] if end != '-' else '-',
                days=max(0, days_left)
            )
            bot.send_message(user_id, sub_info)
        return
    
    # Edit Profile
    if text == t['edit_profile']:
        bot.send_message(user_id, get_text(user_id, 'edit_what'), reply_markup=get_edit_profile_keyboard(user_id))
        return
    
    # Change Language
    if text == t['change_lang']:
        update_user_state(user_id, 'select_language')
        bot.send_message(user_id, "Tilni tanlang / Выберите язык / Choose language:", reply_markup=get_language_keyboard())
        return

    
    # ==================== EDIT PROFILE OPTIONS ====================
    
    if text == t['edit_age']:
        update_user_state(user_id, 'edit_age')
        bot.send_message(user_id, get_text(user_id, 'enter_new_age'), reply_markup=get_back_keyboard(user_id))
        return
    
    if text == t['edit_height']:
        update_user_state(user_id, 'edit_height')
        bot.send_message(user_id, get_text(user_id, 'enter_new_height'), reply_markup=get_back_keyboard(user_id))
        return
    
    if text == t['edit_weight']:
        update_user_state(user_id, 'edit_weight')
        bot.send_message(user_id, get_text(user_id, 'enter_new_weight'), reply_markup=get_back_keyboard(user_id))
        return
    
    if text == t['edit_goal']:
        update_user_state(user_id, 'edit_goal')
        bot.send_message(user_id, get_text(user_id, 'ask_goal'), reply_markup=get_goal_keyboard(user_id))
        return
    
    if text == t['edit_gender']:
        update_user_state(user_id, 'edit_gender')
        bot.send_message(user_id, get_text(user_id, 'ask_gender'), reply_markup=get_gender_keyboard(user_id))
        return
    
    # ==================== DEFAULT: FOOD TEXT ANALYSIS ====================
    # If user sends any other text in main_menu state, treat it as food for analysis
    user = get_user(user_id)
    if user and user[8] == 'main_menu':
        bot.send_message(user_id, get_text(user_id, 'analyzing_food'))
        analysis = analyze_food_text_with_gemini(text, user_id)
        bot.send_message(user_id, analysis, reply_markup=get_food_analysis_keyboard(user_id, text[:20]))


# ============================================================================
# MAIN EXECUTION - OPTIMIZED FOR GOOGLE COLAB AND RENDER
# ============================================================================
def run_bot():
    """Main function to run the bot with error handling"""
    print("=" * 60)
    print("DIET ASSISTANT BOT STARTING...")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Check if tokens are set
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("ERROR: Please set TELEGRAM_BOT_TOKEN environment variable!")
        return
    
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("WARNING: GEMINI_API_KEY not set. AI features may not work.")
    
    print(f"Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"Admin ID: {ADMIN_ID}")
    print("Bot is now running! Send /start to your bot on Telegram.")
    print("=" * 60)
    
    # Start polling with error recovery
    while True:
        try:
            bot.infinity_polling(
                timeout=60,
                long_polling_timeout=60,
                logger_level=None,
                allowed_updates=None,
                skip_pending=True
            )
        except Exception as e:
            print(f"Error occurred: {e}")
            traceback.print_exc()
            print("Restarting in 5 seconds...")
            time.sleep(5)
            continue

# Run the bot only when executed directly (not when imported)
if __name__ == "__main__":
    run_bot()

