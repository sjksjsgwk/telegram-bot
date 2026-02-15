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
    "Türkiye","Almanya","Fransa","ABD","İngiltere","Japonya","Brezilya","İtalya","İspanya","Hollanda",
    "Kanada","Avusturya","Belçika","Norveç","İsveç","Finlandiya","Danimarka","Polonya","Romanya","Bulgaristan"
]

def main_menu_text(user):
    now = datetime.now(TZ).strftime("%d.%m.%Y • %H:%M")
    username = f"@{user.username}" if user.username else user.first_name
    return f"""
✨━━━━━━━━━━━━━━━━━━━━✨
      📲 SMS ONAY SİSTEMİ
✨━━━━━━━━━━━━━━━━━━━━✨

👤 Kullanıcı: {username}
🆔 ID: {user.id}
🕒 Saat: {now}

Aşağıdan işlem seçebilirsin 👇
"""

def main_menu_buttons(uid):
    rows = [
        [InlineKeyboardButton("📩 SMS ONAY", callback_data="sms")],
        [InlineKeyboardButton("👤 HESABIM", callback_data="account"),
         InlineKeyboardButton("📊 İSTATİSTİK", callback_data="stats")],
        [InlineKeyboardButton("🧑‍💻 GELİŞTİRİCİ", callback_data="dev"),
         InlineKeyboardButton("🆘 DESTEK", callback_data="support")]
    ]
    if uid == ADMIN_ID:
        rows.append([InlineKeyboardButton("🔐 ADMIN PANEL", callback_data="admin")])
    return InlineKeyboardMarkup(rows)

async def blocked(update: Update):
    user = update.effective_user
    if user and user.id in DB.banned:
        if update.message:
            await update.message.reply_text("⛔ Bu botu kullanamazsın.")
        elif update.callback_query:
            await update.callback_query.answer("Yasaklısın", show_alert=True)
        return True
    return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await blocked(update):
        return
    user = update.effective_user
    if user.id not in DB.users:
        DB.users[user.id] = {
            "username": f"@{user.username}" if user.username else "Yok",
            "numbers": 0
        }
    await update.message.reply_text(main_menu_text(user), reply_markup=main_menu_buttons(user.id))

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await blocked(update):
        return

    query = update.callback_query
    await query.answer()
    user = query.from_user

    if query.data == "sms":
        sample = random.sample(COUNTRIES, 10)
        rows = [[InlineKeyboardButton(country, callback_data=f"country_{country}")] for country in sample]
        await query.message.reply_text("🌍 Ülke seç:", reply_markup=InlineKeyboardMarkup(rows))

    elif query.data.startswith("country_"):
        country = query.data.split("_", 1)[1]
        DB.waiting_country[user.id] = country
        kb = [[KeyboardButton("📲 NUMARAMI GÖNDER", request_contact=True)]]
        await query.message.reply_text(
            f"{country} seçildi.\nNumaranı göndermek için butona bas.",
            reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True, one_time_keyboard=True)
        )

    elif query.data == "account":
        u = DB.users[user.id]
        await query.message.reply_text(
            f"👤 Kullanıcı: {u['username']}\n🆔 ID: {user.id}\n📨 Gönderim: {u['numbers']}"
        )

    elif query.data == "stats":
        await query.message.reply_text(
            f"📊 Toplam Kullanıcı: {len(DB.users)}\n📲 Toplam Numara: {DB.total_numbers}"
        )

    elif query.data == "dev":
        await query.message.reply_text("🧑‍💻 Geliştirici: @tanrican")

    elif query.data == "support":
        await query.message.reply_text("🆘 Destek için admin ile iletişime geç.")

    elif query.data == "admin" and user.id == ADMIN_ID:
        await query.message.reply_text("🔐 Admin Komutları:\n/ban ID\n/unban ID")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await blocked(update):
        return

    user = update.effective_user
    if user.id not in DB.waiting_country:
        return

    country = DB.waiting_country[user.id]
    del DB.waiting_country[user.id]

    contact: Contact = update.message.contact

    DB.users[user.id]["numbers"] += 1
    DB.total_numbers += 1

    now = datetime.now(TZ).strftime("%d.%m.%Y %H:%M:%S")

    channel_text = f"""
📲 SMS ONAY BİLDİRİMİ

🌍 Ülke: {country}
👤 Kullanıcı: {DB.users[user.id]['username']}
🆔 ID: {user.id}
📱 Numara: +{contact.phone_number}
🕒 Saat: {now}
"""

    await context.bot.send_message(KANAL_ID, channel_text)
    await update.message.reply_text("✅ Numara başarıyla alındı.")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = int(context.args[0])
    DB.banned.add(uid)
    await update.message.reply_text("Banlandı.")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    uid = int(context.args[0])
    DB.banned.discard(uid)
    await update.message.reply_text("Ban kaldırıldı.")

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
