import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# 🟢 مشخصات ایمیل فرستنده — این ۳ مقدار را تغییر بده
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")       # ← ایمیل خودت
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")         # ← App Password گوگل
TOKEN = BOT_TOKEN = os.getenv("TOKEN")            # ← توکن ربات تلگرام

# 🔵 پیام‌های آماده
MESSAGES = {
    "1": "سلام! خوش آمدید 🌟",
    "2": "ما خدمات طراحی سایت، سئو و تولید محتوا ارائه می‌دهیم.",
    "3": "از اعتماد شما سپاسگزاریم 🙏"
}

# 🔐 ذخیره ایمیل موقت کاربر
user_email_map = {}

# ✉️ ارسال ایمیل
def send_email(to_email, message):
    msg = MIMEMultipart()
    msg['From'] = f"Ali Sabour <{EMAIL_ADDRESS}>"
    msg['To'] = to_email
    msg['Subject'] = "پیام خودکار"

    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# ⬅️ شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفاً فقط آدرس ایمیل را ارسال کنید.")

# 📥 دریافت ایمیل از کاربر
async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if "@" not in text or "." not in text:
        await update.message.reply_text("❌ ایمیل وارد شده معتبر نیست.")
        return

    user_id = update.message.from_user.id
    user_email_map[user_id] = text  # ذخیره ایمیل موقتاً

    # ساخت دکمه‌ها
    keyboard = [
        [InlineKeyboardButton(f"{key}. {value[:30]}...", callback_data=key)]
        for key, value in MESSAGES.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("کدام پیام را می‌خواهید برای این ایمیل ارسال کنم؟", reply_markup=reply_markup)

# 📌 وقتی کاربر روی دکمه کلیک کند
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    msg_id = query.data
    user_id = query.from_user.id
    to_email = user_email_map.get(user_id)

    if not to_email:
        await query.edit_message_text("❌ ایمیل یافت نشد. لطفاً دوباره ایمیل ارسال کنید.")
        return

    message_to_send = MESSAGES.get(msg_id)
    try:
        send_email(to_email, message_to_send)
        await query.edit_message_text(f"✅ پیام شماره {msg_id} با موفقیت به {to_email} ارسال شد.")
        del user_email_map[user_id]
    except Exception as e:
        await query.edit_message_text(f"❌ خطا در ارسال ایمیل:\n{e}")

# ▶️ راه‌اندازی ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
