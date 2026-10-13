import os, json, threading, datetime
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ.get("BOT_TOKEN")
# --- إعداداتك انت تعدلها من Render > Environment ---
WHATSAPP = os.environ.get("WHATSAPP", "9665XXXXXXXX") # رقمك بدون +
CHANNEL = os.environ.get("CHANNEL", "") # مثال @qanatak بدون @ اذا ما تبي اشتراك اجباري خله فاضي
FREE_DAYS = int(os.environ.get("FREE_DAYS", "0")) # 0 = مفتوح، 365 = سنة، 30 = شهر

bot = telebot.TeleBot(TOKEN)
DB_FILE = "db.json"

app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000))), daemon=True).start()

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE,'r',encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}
def save_db(d):
    with open(DB_FILE,'w',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False)

def is_subscribed(user_id):
    if not CHANNEL: return True
    try:
        m = bot.get_chat_member(f"@{CHANNEL}", user_id)
        return m.status in ['member','administrator','creator']
    except: return True

def check_free(user_data):
    if FREE_DAYS == 0: return True
    first = user_data.get('first_join')
    if not first: return True
    first_date = datetime.datetime.fromisoformat(first)
    return (datetime.datetime.now() - first_date).days <= FREE_DAYS

def main_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    btns = []
    if CHANNEL:
        btns.append(InlineKeyboardButton("🔔 اشترك بالقناة", url=f"https://t.me/{CHANNEL}"))
    btns.append(InlineKeyboardButton("💬 تواصل واتساب", url=f"https://wa.me/{WHATSAPP}"))
    markup.add(*btns)
    markup.add(InlineKeyboardButton("📁 ملفاتي", callback_data="storage"),
               InlineKeyboardButton("🆘 مساعدة", callback_data="help"))
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    db = load_db()
    uid = str(m.chat.id)
    if uid not in db:
        db[uid] = {"files":[],"first_join":datetime.datetime.now().isoformat()}
        save_db(db)

    if not is_subscribed(m.chat.id):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔔 اشترك بالقناة", url=f"https://t.me/{CHANNEL}"))
        markup.add(InlineKeyboardButton("✅ تحققت اشتركت", callback_data="check_sub"))
        bot.send_message(m.chat.id, f"⚠️ عشان تستخدم البوت لازم تشترك أولاً في قناتنا @{CHANNEL}", reply_markup=markup)
        return