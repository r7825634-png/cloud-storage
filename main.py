import os, json, threading
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("ERROR: BOT_TOKEN not set!")
    exit(1)

WHATSAPP = os.getenv("WHATSAPP", "967782562438")
CHANNEL = os.getenv("CHANNEL", "")
FREE_DAYS_STR = os.getenv("FREE_DAYS", "0")
try:
    FREE_DAYS = int(FREE_DAYS_STR)
except:
    FREE_DAYS = 0

bot = telebot.TeleBot(TOKEN)

# تغيير أزرار التحكم للعربي
try:
    bot.set_my_commands([
        telebot.types.BotCommand("start", "☁️ التخزين السحابي"),
        telebot.types.BotCommand("storage", "📁 ملفاتي"),
        telebot.types.BotCommand("search", "🔍 البحث عن ملف"),
        telebot.types.BotCommand("stats", "📊 إحصائياتي"),
        telebot.types.BotCommand("help", "🆘 المساعدة"),
    ])
    print("Commands set to Arabic")
except Exception as e:
    print(f"Could not set commands: {e}")

app = Flask(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive - cloud-storage"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_flask, daemon=True).start()

DB_FILE = "db.json"
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE,'r',encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}
def save_db(d):
    with open(DB_FILE,'w',encoding='utf-8') as f: json.dump(d,f,ensure_ascii=False)

def main_kb():
    kb = InlineKeyboardMarkup()
    if CHANNEL:
        kb.add(InlineKeyboardButton("🔔 اشترك بالقناة", url=f"https://t.me/{CHANNEL}"))
    kb.add(InlineKeyboardButton("💬 تواصل واتساب", url=f"https://wa.me/{WHATSAPP}"))
    return kb

@bot.message_handler(commands=['start','help','storage','search','stats'])
def commands(m):
    db = load_db()
    uid = str(m.chat.id)
    if uid not in db:
        db[uid] = []

    txt = m.text or ""
    if txt.startswith('/start'):
        save_db(db)
        bot.send_message(m.chat.id, f"☁️ أهلا بك في التخزين السحابي!\n\n📱 واتساب: {WHATSAPP}\n📁 أرسل أي ملف لحفظه\n\n/storage - ملفاتي\n/search - بحث\n/help - مساعدة", reply_markup=main_kb())
    elif txt.startswith('/storage'):
        files = db.get(uid, [])
        if not files:
            bot.send_message(m.chat.id, "📁 ملفاتك فاضية")
        else:
            bot.send_message(m.chat.id, f"📁 عندك {len(files)} ملف")
            for f in files[-10:]:
                try:
                    if f.get('type') == 'photo': bot.send_photo(m.chat.id, f['id'], caption=f['name'])
                    else: bot.send_document(m.chat.id, f['id'], caption=f['name'])
                except: pass
    elif txt.startswith('/help'):
        bot.send_message(m.chat.id, "🆘 الأوامر:\n/start البداية\n/storage ملفاتي\n/search اسم الملف\n/stats إحصائيات\n\nللتواصل اضغط زر واتساب", reply_markup=main_kb())
    elif txt.startswith('/stats'):
        files = db.get(uid, [])
        bot.send_message(m.chat.id, f"📊 عدد ملفاتك: {len(files)}\nالمدة المجانية: {'مفتوحة' if FREE_DAYS==0 else f'{FREE_DAYS} يوم'}")
    elif txt.startswith('/search'):
        q = txt.replace('/search','').strip().lower()
        if not q:
            bot.send_message(m.chat.id, "اكتب: /search اسم الملف")
            return
        files = db.get(uid, [])
        found = [f for f in files if q in f.get('name','').lower()]
        if not found: bot.send_message(m.chat.id, "❌ ما لقيت")
        else:
            for f in found[:10]:
                try:
                    if f.get('type') == 'photo': bot.send_photo(m.chat.id, f['id'], caption=f['name'])
                    else: bot.send_document(m.chat.id, f['id'], caption=f['name'])
                except: pass

@bot.message_handler(content_types=['document','photo','video'])
def handle_files(m):
    db = load_db()
    uid = str(m.chat.id)
    if uid not in db: db[uid] = []
    fid, ftype, fname = None, "doc", "ملف"
    if m.document: fid, fname = m.document.file_id, m.document.file_name
    elif m.photo: fid, ftype, fname = m.photo[-1].file_id, "photo", f"صورة_{len(db[uid])+1}.jpg"
    elif m.video: fid, ftype, fname = m.video.file_id, "video", "فيديو.mp4"
    if fid:
        db[uid].append({"id":fid,"name":fname,"type":ftype})
        save_db(db)
        bot.reply_to(m, f"✅ تم حفظ {fname}", reply_markup=main_kb())

print("Bot starting...")
bot.infinity_polling()
