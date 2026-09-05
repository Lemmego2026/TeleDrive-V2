import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = "توکن_شما"
GITHUB_TOKEN = "توکن_گیت‌هاب_شما"
REPO_OWNER = "نام_کاربری"
REPO_NAME = "TeleDrive-V2"

# در صورت نیاز پروکسی را فعال کنید
# import os
# os.environ["HTTP_PROXY"] = "socks5://127.0.0.1:10808"
# os.environ["HTTPS_PROXY"] = "socks5://127.0.0.1:10808"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ لطفا یک لینک معتبر بفرستید.")
        return

    await update.message.reply_text("⏳ درخواست به گیت‌هاب ارسال شد...")
    
    gh_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/dispatches"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {
        "event_type": "download_link",
        "client_payload": {"file_url": url, "telegram_chat_id": str(update.message.chat_id)}
    }

    try:
        res = requests.post(gh_url, json=payload, headers=headers)
        if res.status_code == 204:
            await update.message.reply_text("🚀 سرور ابری روشن شد! نتیجه به زودی ارسال می‌شود.")
        else:
            await update.message.reply_text("❌ خطا در اجرای سرور گیت‌هاب.")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("🤖 ربات روشن شد...")
    app.run_polling()
