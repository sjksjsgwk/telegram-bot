import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
KANAL_ID = int(os.getenv("KANAL_ID"))

waiting_number = set()
banned_users = set()

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📲 SMS Onay", callback_data="sms")],
        [InlineKeyboardButton("👤 Profilim", callback_data="profil")],
        [InlineKeyboardButton("ℹ️ Yardım", callback_data="yardim")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in banned_users:
        return
    await update.message.reply_text(
        f"Hoşgeldin {user.first_name}",
        reply_markup=main_menu()
    )

async def menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    if user.id in banned_users:
        return
    await query.answer()

    if query.data == "sms":
        waiting_number.add(user.id)
        btn = KeyboardButton("Numara Gönder", request_contact=True)
        kb = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)
        await query.message.reply_text("Telefon numaranı gönder", reply_markup=kb)

    elif query.data == "profil":
        await query.message.reply_text(f"ID: {user.id}\nAd: {user.first_name}")

    elif query.data == "yardim":
        await query.message.reply_text("Menüden SMS Onay seçip numaranı gönder")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in waiting_number:
        return

    waiting_number.remove(user.id)

    phone = update.message.contact.phone_number
    code = random.randint(100000,999999)

    time = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y %H:%M:%S")

    await update.message.reply_text(f"Onay kodun: {code}")

    text = f"""
Yeni SMS Onay
Kullanıcı: {user.first_name}
ID: {user.id}
Numara: {phone}
Kod: {code}
Saat: {time}
"""
    await context.bot.send_message(chat_id=KANAL_ID, text=text)

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        return
    uid = int(context.args[0])
    banned_users.add(uid)
    await update.message.reply_text("Banlandı")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        return
    uid = int(context.args[0])
    banned_users.discard(uid)
    await update.message.reply_text("Ban kaldırıldı")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        return
    msg = " ".join(context.args)
    for uid in list(waiting_number):
        try:
            await context.bot.send_message(uid, msg)
        except:
            pass
    await update.message.reply_text("Gönderildi")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ban", ban))
app.add_handler(CommandHandler("unban", unban))
app.add_handler(CommandHandler("duyuru", broadcast))
app.add_handler(CallbackQueryHandler(menu_buttons))
app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

app.run_polling()
