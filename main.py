import os, json, threading
from flask import Flask
import telebot

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
DB_FILE = "db.json"

# سيرفر وهمي مجاني عشان Render ما يطفيك
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Alive!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
threading.Thread(target=run_flask, daemon=True).start()

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}
def save_db(d):
    with open(DB_FILE, 'w', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False)

@bot.message_handler(commands=['start','storage','stats'])
def cmds(m):
    db = load_db()
    uid = str(m.chat.id)
    files = db.get(uid, [])
    if m.text.startswith('/start'):
        if uid not in db: db[uid] = []; save_db(db)
        bot.send_message(m.chat.id, f"☁️ التخزين السحابي\nملفاتك: {len(files)}\nأرسل أي ملف الآن")
    elif m.text.startswith('/storage'):
        if not files: bot.send_message(m.chat.id, "📁 فاضي"); return
        bot.send_message(m.chat.id, f"📁 عندك {len(files)} ملف:")
        for f in files[-10:]:
            try:
                if f['type'] == 'photo': bot.send_photo(m.chat.id, f['id'])
                else: bot.send_document(m.chat.id, f['id'], caption=f['name'])
            except: pass
    elif m.text.startswith('/stats'):
        bot.send_message(m.chat.id, f"📊 عدد الملفات: {len(files)}")

@bot.message_handler(content_types=['document','photo','video','audio','voice'])
def save_file(m):
    db = load_db()
    uid = str(m.chat.id)
    if uid not in db: db[uid] = []
    file_id, f_type, f_name = None, "doc", "ملف"
    if m.document: file_id, f_type, f_name = m.document.file_id, "doc", m.document.file_name
    elif m.photo: file_id, f_type, f_name = m.photo[-1].file_id, "photo", f"صورة_{len(db[uid])+1}.jpg"
    elif m.video: file_id, f_type, f_name = m.video.file_id, "video", "فيديو"
    elif m.audio: file_id, f_type, f_name = m.audio.file_id, "audio", "صوت"
    if file_id:
        db[uid].append({"id": file_id, "name": f_name, "type": f_type})
        save_db(db)
        bot.reply_to(m, f"✅ تم حفظ {f_name}")

bot.infinity_polling()