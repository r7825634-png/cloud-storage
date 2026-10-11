import os, json
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID") # اختياري، سنشرحه تحت

bot = telebot.TeleBot(TOKEN)
DB_FILE = "db.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return {}
    return {}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

@bot.message_handler(commands=['start'])
def start(m):
    db = load_db()
    uid = str(m.chat.id)
    if uid not in db:
        db[uid] = []
        save_db(db)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📁 ملفاتي المحفوظة", callback_data="show_storage"))
    markup.add(types.InlineKeyboardButton("📊 إحصائياتي", callback_data="show_stats"), types.InlineKeyboardButton("🆘 مساعدة", callback_data="show_help"))

    bot.send_message(m.chat.id, f"☁️ **أهلاً بك في التخزين السحابي غير المحدود**\n\nأرسل أي ملف الآن وسأحفظه لك للأبد.\nحتى لو حذفت تليجرام ورجعت، راح تلاقيه.\n\n📦 عدد ملفاتك حالياً: {len(db.get(uid, []))}", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(content_types=['document','photo','video','audio','voice','video_note'])
def save_file(m):
    db = load_db()
    uid = str(m.chat.id)
    if uid not in db: db[uid] = []

    file_id = None
    file_name = "ملف"
    if m.document:
        file_id = m.document.file_id
        file_name = m.document.file_name
    elif m.photo:
        file_id = m.photo[-1].file_id
        file_name = f"صورة_{m.photo[-1].file_id[:5]}.jpg"
    elif m.video:
        file_id = m.video.file_id
        file_name = m.video.file_name or "فيديو.mp4"
    elif m.audio:
        file_id = m.audio.file_id
        file_name = m.audio.file_name or "صوت.mp3"

    if file_id:
        db[uid].append({"id": file_id, "name": file_name})
        save_db(db)
        bot.reply_to(m, f"✅ تم حفظ **{file_name}**\nلن ينحذف إلا يدوياً.", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "show_storage":
        m = call.message
        m.text = "/storage"
        handle_storage(m)
    elif call.data == "show_stats":
        m = call.message
        m.text = "/stats"
        handle_storage(m)
    elif call.data == "show_help":
        bot.send_message(call.message.chat.id, "🆘 أرسل أي ملف لحفظه.\n/storage - لعرض ملفاتك\n/search - للبحث\n/stats - للإحصائيات")

@bot.message_handler(commands=['storage','stats','search','help'])
def handle_storage(m):
    db = load_db()
    uid = str(m.chat.id)
    files = db.get(uid, [])

    if m.text.startswith('/storage'):
        if not files:
            bot.send_message(m.chat.id, "📁 مخزنك فاضي، أرسل أي ملف الآن")
            return
        bot.send_message(m.chat.id, f"📁 عندك {len(files)} ملف. هذه آخر 10:")
        for f in files[-10:]:
            try:
                bot.send_document(m.chat.id, f['id'], caption=f"📄 {f['name']}")
            except:
                bot.send_message(m.chat.id, f"📄 {f['name']}")
    elif m.text.startswith('/stats'):
        bot.send_message(m.chat.id, f"📊 إحصائياتك:\nعدد الملفات: {len(files)}\nنوع التخزين: تليجرام غير محدود ☁️")
    elif m.text.startswith('/search'):
        bot.send_message(m.chat.id, "🔍 أرسل اسم الملف للبحث عنه (هذه الميزة قيد التطوير)")
    elif m.text.startswith('/help'):
        bot.send_message(m.chat.id, "🆘 فقط أرسل الملفات هنا")

bot.infinity_polling()