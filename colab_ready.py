TELEGRAM_BOT_TOKEN = "8163772583:AAFY4g1M8OS4luohuvrMYpqJ6fa32ue8zvc"
GEMINI_API_KEY = "AIzaSyAb8RN6J_yF03nQqGXE4vivuqZQxW0uOknWRw0cseErYLij5DLw"
ADMIN_ID = 956947665

import telebot
from telebot import types
import sqlite3
import google.generativeai as genai
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

LANG = {
    "uz": {
        "welcome": "Salom! Yoshingiz nechida?",
        "ask_height": "Boyingizni kiriting (170):",
        "ask_weight": "Vazningizni kiriting (70):",
        "ask_goal": "Maqsadingiz:",
        "ask_gender": "Jinsingiz:",
        "done": "Royxatdan otdingiz! 3 kun bepul.",
        "goal_lose": "Ozish",
        "goal_gain": "Vazn olish",
        "goal_keep": "Saqlash",
        "male": "Erkak",
        "female": "Ayol",
        "vip_only": "Faqat VIP uchun!",
        "ration": "Ratsion",
        "report": "Hisobot",
        "water": "Suv",
        "ai": "AI Chat",
        "profile": "Profil",
        "vip": "VIP olish",
        "back": "Orqaga",
        "drank": "Ichdim",
        "stats": "Statistika",
        "eat": "Yeyman",
        "pay_info": "Karta: 9860040114589092\nNarx: 20000\nTolovdan song /chek",
        "receipt_ok": "Chek qabul qilindi!",
        "vip_on": "VIP faol!",
        "water_rec": "Kuniga {l} litr suv kerak",
        "water_add": "250ml qoshildi! Bugun: {t} ml",
        "no_data": "Malumot yoq",
        "analyzing": "Tahlil qilinmoqda...",
        "food_ok": "Saqlandi!",
        "about": "Haqida",
        "sub": "Obuna",
        "edit": "Tahrir",
        "lang": "Til"
    },
    "ru": {
        "welcome": "Привет! Сколько вам лет?",
        "ask_height": "Введите рост (170):",
        "ask_weight": "Введите вес (70):",
        "ask_goal": "Ваша цель:",
        "ask_gender": "Ваш пол:",
        "done": "Регистрация завершена! 3 дня бесплатно.",
        "goal_lose": "Похудеть",
        "goal_gain": "Набрать",
        "goal_keep": "Держать",
        "male": "Мужчина",
        "female": "Женщина",
        "vip_only": "Только VIP!",
        "ration": "Рацион",
        "report": "Отчет",
        "water": "Вода",
        "ai": "AI Чат",
        "profile": "Профиль",
        "vip": "VIP",
        "back": "Назад",
        "drank": "Выпил",
        "stats": "Стат",
        "eat": "Съем",
        "pay_info": "Карта: 9860040114589092\nЦена: 20000\nПосле оплаты /chek",
        "receipt_ok": "Чек получен!",
        "vip_on": "VIP активен!",
        "water_rec": "Нужно {l} л воды в день",
        "water_add": "250мл добавлено! Сегодня: {t} мл",
        "no_data": "Нет данных",
        "analyzing": "Анализ...",
        "food_ok": "Сохранено!",
        "about": "О себе",
        "sub": "Подписка",
        "edit": "Изменить",
        "lang": "Язык"
    },
    "en": {
        "welcome": "Hi! How old are you?",
        "ask_height": "Enter height (170):",
        "ask_weight": "Enter weight (70):",
        "ask_goal": "Your goal:",
        "ask_gender": "Your gender:",
        "done": "Registered! 3 days free.",
        "goal_lose": "Lose",
        "goal_gain": "Gain",
        "goal_keep": "Keep",
        "male": "Male",
        "female": "Female",
        "vip_only": "VIP only!",
        "ration": "Ration",
        "report": "Report",
        "water": "Water",
        "ai": "AI Chat",
        "profile": "Profile",
        "vip": "VIP",
        "back": "Back",
        "drank": "Drank",
        "stats": "Stats",
        "eat": "Eat",
        "pay_info": "Card: 9860040114589092\nPrice: 20000\nAfter payment /chek",
        "receipt_ok": "Receipt received!",
        "vip_on": "VIP active!",
        "water_rec": "Need {l} L water daily",
        "water_add": "250ml added! Today: {t} ml",
        "no_data": "No data",
        "analyzing": "Analyzing...",
        "food_ok": "Saved!",
        "about": "About",
        "sub": "Sub",
        "edit": "Edit",
        "lang": "Lang"
    }
}

def init_db():
    c = sqlite3.connect("bot.db")
    c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,lang TEXT DEFAULT 'uz',age INT,height REAL,weight REAL,goal TEXT,gender TEXT,state TEXT,vip INT DEFAULT 0,created TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS water(id INTEGER PRIMARY KEY,uid INT,ml INT,date TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS food(id INTEGER PRIMARY KEY,uid INT,name TEXT,kcal REAL,date TEXT)")
    c.commit()
    c.close()

def get_user(uid):
    c = sqlite3.connect("bot.db")
    r = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c.close()
    return r

def save(uid, field, val):
    c = sqlite3.connect("bot.db")
    c.execute("UPDATE users SET " + field + "=? WHERE id=?", (val, uid))
    c.commit()
    c.close()

def create_user(uid):
    c = sqlite3.connect("bot.db")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT OR IGNORE INTO users(id,state,created) VALUES(?,?,?)", (uid, "lang", now))
    c.commit()
    c.close()

def T(uid, key):
    u = get_user(uid)
    lang = u[1] if u else "uz"
    return LANG.get(lang, LANG["uz"]).get(key, key)

def is_vip(uid):
    u = get_user(uid)
    if not u:
        return False
    if u[8] == 1:
        return True
    if u[9]:
        created = datetime.strptime(u[9], "%Y-%m-%d %H:%M:%S")
        return (datetime.now() - created).days < 3
    return False

def calc_water(uid):
    u = get_user(uid)
    w = u[4] if u and u[4] else 70
    return round(w * 0.033, 1)

def get_water(uid):
    c = sqlite3.connect("bot.db")
    today = datetime.now().strftime("%Y-%m-%d")
    r = c.execute("SELECT SUM(ml) FROM water WHERE uid=? AND date LIKE ?", (uid, today + "%")).fetchone()
    c.close()
    return r[0] if r[0] else 0

def add_water(uid):
    c = sqlite3.connect("bot.db")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO water(uid,ml,date) VALUES(?,?,?)", (uid, 250, now))
    c.commit()
    c.close()

def kb_lang():
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("Uzbek", callback_data="uz"))
    k.add(types.InlineKeyboardButton("Russian", callback_data="ru"))
    k.add(types.InlineKeyboardButton("English", callback_data="en"))
    return k

def kb_goal(uid):
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(T(uid, "goal_lose"), T(uid, "goal_gain"), T(uid, "goal_keep"))
    return k

def kb_gender(uid):
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(T(uid, "male"), T(uid, "female"))
    return k

def kb_main(uid):
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(T(uid, "ration"), T(uid, "report"))
    k.add(T(uid, "water"), T(uid, "ai"))
    k.add(T(uid, "profile"), T(uid, "vip"))
    return k

def kb_profile(uid):
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(T(uid, "about"), T(uid, "sub"))
    k.add(T(uid, "edit"), T(uid, "lang"))
    k.add(T(uid, "back"))
    return k

def kb_water(uid):
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton(T(uid, "drank"), callback_data="drink"))
    k.add(types.InlineKeyboardButton(T(uid, "stats"), callback_data="wstat"))
    return k

def kb_food(uid):
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton(T(uid, "eat"), callback_data="logfood"))
    return k

def kb_back(uid):
    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(T(uid, "back"))
    return k

def kb_vip(uid):
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("Chek yuborish", callback_data="sendchek"))
    return k

def kb_admin(uid):
    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton("VIP berish", callback_data="setvip:" + str(uid)))
    return k

def ai_analyze(text, uid):
    u = get_user(uid)
    lang = u[1] if u else "uz"
    if lang == "uz":
        prompt = "Uzbek tilida javob ber. "
    elif lang == "ru":
        prompt = "Otvet po russki. "
    else:
        prompt = "Answer in English. "
    prompt = prompt + "Analyze food: " + text + ". Give: name, weight(g), calories(kcal), protein/carbs/fat. Short answer."
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return str(e)

def ai_image(img, uid):
    u = get_user(uid)
    lang = u[1] if u else "uz"
    if lang == "uz":
        prompt = "Uzbek tilida javob ber. "
    elif lang == "ru":
        prompt = "Otvet po russki. "
    else:
        prompt = "Answer in English. "
    prompt = prompt + "Analyze this food image. Give: name, weight(g), calories(kcal). Short answer."
    try:
        return model.generate_content([prompt, img]).text
    except Exception as e:
        return str(e)

def ai_chat(text, uid):
    u = get_user(uid)
    lang = u[1] if u else "uz"
    if lang == "uz":
        prompt = "Uzbek tilida javob ber. "
    elif lang == "ru":
        prompt = "Otvet po russki. "
    else:
        prompt = "Answer in English. "
    prompt = prompt + "You are a dietitian. Answer about nutrition only: " + text
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return str(e)

def ai_ration(uid):
    u = get_user(uid)
    lang = u[1] if u else "uz"
    w = u[4] if u and u[4] else 70
    goal = u[5] if u else "keep"
    kcal = int(w * 30)
    if lang == "uz":
        prompt = "Uzbek tilida javob ber. "
    elif lang == "ru":
        prompt = "Otvet po russki. "
    else:
        prompt = "Answer in English. "
    prompt = prompt + str(kcal) + " kcal meal plan: breakfast, lunch, dinner. Goal: " + str(goal) + ". Short."
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return str(e)

@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id
    create_user(uid)
    save(uid, "state", "lang")
    bot.send_message(uid, "Tilni tanlang:", reply_markup=kb_lang())

@bot.message_handler(commands=["chek"])
def chek(m):
    uid = m.from_user.id
    save(uid, "state", "chek")
    bot.send_message(uid, "Chek rasmini yuboring:", reply_markup=kb_back(uid))

@bot.message_handler(commands=["user"])
def users(m):
    if m.from_user.id != ADMIN_ID:
        return
    c = sqlite3.connect("bot.db")
    total = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    vips = c.execute("SELECT COUNT(*) FROM users WHERE vip=1").fetchone()[0]
    c.close()
    bot.send_message(ADMIN_ID, "Jami: " + str(total) + "\nVIP: " + str(vips))

@bot.message_handler(commands=["reklama"])
def ads(m):
    if m.from_user.id != ADMIN_ID:
        return
    save(ADMIN_ID, "state", "ads")
    bot.send_message(ADMIN_ID, "Reklama xabarini yuboring:")

@bot.callback_query_handler(func=lambda c: c.data in ["uz", "ru", "en"])
def setlang(c):
    uid = c.from_user.id
    save(uid, "lang", c.data)
    save(uid, "state", "age")
    bot.answer_callback_query(c.id)
    bot.send_message(uid, T(uid, "welcome"))

@bot.callback_query_handler(func=lambda c: c.data == "drink")
def drink(c):
    uid = c.from_user.id
    if not is_vip(uid):
        bot.answer_callback_query(c.id, T(uid, "vip_only"), show_alert=True)
        return
    add_water(uid)
    t = get_water(uid)
    bot.answer_callback_query(c.id, T(uid, "water_add").format(t=t))

@bot.callback_query_handler(func=lambda c: c.data == "wstat")
def wstat(c):
    uid = c.from_user.id
    t = get_water(uid)
    target = int(calc_water(uid) * 1000)
    bot.answer_callback_query(c.id)
    bot.send_message(uid, "Bugun: " + str(t) + " ml / " + str(target) + " ml")

@bot.callback_query_handler(func=lambda c: c.data == "logfood")
def logfood(c):
    uid = c.from_user.id
    bot.answer_callback_query(c.id, T(uid, "food_ok"))

@bot.callback_query_handler(func=lambda c: c.data == "sendchek")
def sendchek(c):
    uid = c.from_user.id
    save(uid, "state", "chek")
    bot.answer_callback_query(c.id)
    bot.send_message(uid, "Chek rasmini yuboring:", reply_markup=kb_back(uid))

@bot.callback_query_handler(func=lambda c: c.data.startswith("setvip:"))
def setvip(c):
    if c.from_user.id != ADMIN_ID:
        bot.answer_callback_query(c.id, "No")
        return
    uid = int(c.data.split(":")[1])
    save(uid, "vip", 1)
    bot.answer_callback_query(c.id, "VIP!")
    bot.send_message(uid, T(uid, "vip_on"), reply_markup=kb_main(uid))

@bot.message_handler(content_types=["photo"])
def photo(m):
    uid = m.from_user.id
    u = get_user(uid)
    state = u[7] if u else None
    
    if state == "chek":
        bot.forward_message(ADMIN_ID, uid, m.message_id)
        bot.send_message(ADMIN_ID, "Chek: " + str(uid), reply_markup=kb_admin(uid))
        bot.send_message(uid, T(uid, "receipt_ok"), reply_markup=kb_main(uid))
        save(uid, "state", "main")
        return
    
    if state == "ads" and uid == ADMIN_ID:
        c = sqlite3.connect("bot.db")
        users = c.execute("SELECT id FROM users").fetchall()
        c.close()
        for u in users:
            try:
                bot.send_photo(u[0], m.photo[-1].file_id, caption=m.caption)
            except:
                pass
        bot.send_message(ADMIN_ID, "Yuborildi: " + str(len(users)))
        save(ADMIN_ID, "state", "main")
        return
    
    bot.send_message(uid, T(uid, "analyzing"))
    f = bot.get_file(m.photo[-1].file_id)
    d = bot.download_file(f.file_path)
    img = Image.open(BytesIO(d))
    r = ai_image(img, uid)
    bot.send_message(uid, r, reply_markup=kb_food(uid))

@bot.message_handler(func=lambda m: True)
def text(m):
    uid = m.from_user.id
    txt = m.text
    u = get_user(uid)
    state = u[7] if u else None
    
    if txt == T(uid, "back"):
        save(uid, "state", "main")
        bot.send_message(uid, "Menu:", reply_markup=kb_main(uid))
        return
    
    if state == "age":
        try:
            age = int(txt)
            if 7 <= age <= 80:
                save(uid, "age", age)
                save(uid, "state", "height")
                bot.send_message(uid, T(uid, "ask_height"))
        except:
            pass
        return
    
    if state == "height":
        try:
            h = float(txt)
            if 50 <= h <= 250:
                save(uid, "height", h)
                save(uid, "state", "weight")
                bot.send_message(uid, T(uid, "ask_weight"))
        except:
            pass
        return
    
    if state == "weight":
        try:
            w = float(txt)
            if 20 <= w <= 300:
                save(uid, "weight", w)
                save(uid, "state", "goal")
                bot.send_message(uid, T(uid, "ask_goal"), reply_markup=kb_goal(uid))
        except:
            pass
        return
    
    if state == "goal":
        goals = {T(uid, "goal_lose"): "lose", T(uid, "goal_gain"): "gain", T(uid, "goal_keep"): "keep"}
        if txt in goals:
            save(uid, "goal", goals[txt])
            save(uid, "state", "gender")
            bot.send_message(uid, T(uid, "ask_gender"), reply_markup=kb_gender(uid))
        return
    
    if state == "gender":
        genders = {T(uid, "male"): "male", T(uid, "female"): "female"}
        if txt in genders:
            save(uid, "gender", genders[txt])
            save(uid, "state", "main")
            bot.send_message(uid, T(uid, "done"), reply_markup=kb_main(uid))
        return
    
    if state == "ai_chat":
        r = ai_chat(txt, uid)
        bot.send_message(uid, r, reply_markup=kb_back(uid))
        return
    
    if state == "ads" and uid == ADMIN_ID:
        c = sqlite3.connect("bot.db")
        users = c.execute("SELECT id FROM users").fetchall()
        c.close()
        for u in users:
            try:
                bot.send_message(u[0], txt)
            except:
                pass
        bot.send_message(ADMIN_ID, "Yuborildi: " + str(len(users)))
        save(ADMIN_ID, "state", "main")
        return
    
    if txt == T(uid, "ration"):
        if not is_vip(uid):
            bot.send_message(uid, T(uid, "vip_only"))
            return
        bot.send_message(uid, T(uid, "analyzing"))
        r = ai_ration(uid)
        bot.send_message(uid, r)
        return
    
    if txt == T(uid, "report"):
        if not is_vip(uid):
            bot.send_message(uid, T(uid, "vip_only"))
            return
        bot.send_message(uid, T(uid, "no_data"))
        return
    
    if txt == T(uid, "water"):
        if not is_vip(uid):
            bot.send_message(uid, T(uid, "vip_only"))
            return
        l = calc_water(uid)
        bot.send_message(uid, T(uid, "water_rec").format(l=l), reply_markup=kb_water(uid))
        return
    
    if txt == T(uid, "ai"):
        if not is_vip(uid):
            bot.send_message(uid, T(uid, "vip_only"))
            return
        save(uid, "state", "ai_chat")
        bot.send_message(uid, "Savol bering:", reply_markup=kb_back(uid))
        return
    
    if txt == T(uid, "profile"):
        bot.send_message(uid, "Profil:", reply_markup=kb_profile(uid))
        return
    
    if txt == T(uid, "vip"):
        bot.send_message(uid, T(uid, "pay_info"), reply_markup=kb_vip(uid))
        return
    
    if txt == T(uid, "about"):
        u = get_user(uid)
        if u:
            info = "Yosh: " + str(u[2]) + "\nBoy: " + str(u[3]) + "\nVazn: " + str(u[4]) + "\nMaqsad: " + str(u[5])
            bot.send_message(uid, info)
        return
    
    if txt == T(uid, "sub"):
        status = "VIP" if is_vip(uid) else "Free"
        bot.send_message(uid, "Status: " + status)
        return
    
    if txt == T(uid, "edit"):
        save(uid, "state", "age")
        bot.send_message(uid, T(uid, "welcome"))
        return
    
    if txt == T(uid, "lang"):
        save(uid, "state", "lang")
        bot.send_message(uid, "Til:", reply_markup=kb_lang())
        return
    
    if state == "main":
        bot.send_message(uid, T(uid, "analyzing"))
        r = ai_analyze(txt, uid)
        bot.send_message(uid, r, reply_markup=kb_food(uid))

init_db()
print("Bot ishga tushdi!")
bot.infinity_polling()
