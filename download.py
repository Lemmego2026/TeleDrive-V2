import os
import sys
import json
import requests
from urllib.parse import urlparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# دریافت متغیرهای محیطی از گیت‌هاب اکشن
FILE_URL = os.environ.get("FILE_URL")
TG_BOT = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID")
GDRIVE_JSON = os.environ.get("GDRIVE_CREDENTIALS")
FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

def send_tg(msg):
    """تابع ساده برای ارسال پیام به تلگرام"""
    url = f"https://api.telegram.org/bot{TG_BOT}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHAT, "text": msg})

def main():
    if not FILE_URL:
        sys.exit(1)

    # استخراج ساده اسم فایل از انتهای لینک
    filename = os.path.basename(urlparse(FILE_URL).path)
    if not filename:
        filename = "downloaded_file.dat"
    
    file_path = f"./{filename}"
    send_tg(f"⏳ شروع دانلود فایل:\n`{filename}`")

    try:
        # مرحله ۱: دانلود فایل از لینک مبدأ روی سرور گیت‌هاب
        with requests.get(FILE_URL, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        send_tg("📦 دانلود تمام شد. در حال آپلود به گوگل درایو شخصی شما...")

        # مرحله ۲: اتصال به گوگل درایو با توکن کاربری (OAuth 2.0)
        creds = Credentials.from_authorized_user_info(
            json.loads(GDRIVE_JSON), 
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds, cache_discovery=False)

        # مرحله ۳: آپلود یکپارچه فایل
        file_metadata = {"name": filename, "parents": [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=False) 
        
        drive_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="webViewLink",
            supportsAllDrives=True
        ).execute()

        link = drive_file.get("webViewLink")
        send_tg(f"✅ فایل با موفقیت در درایو شما ذخیره شد!\n🔗 لینک مشاهده:\n{link}")

    except Exception as e:
        # در صورت بروز هرگونه ارور
        send_tg(f"❌ خطا در عملیات:\n`{str(e)}`\n\n🗑 فایل ناقص حذف شد.")
        sys.exit(1)
        
    finally:
        # مرحله ۴: پاکسازی فایل از روی سرور گیت‌هاب (جلوگیری از پر شدن فضا)
        if os.path.exists(file_path):
            os.remove(file_path)
            print("🧹 فایل لوکال پاکسازی شد.")

if __name__ == "__main__":
    main()
