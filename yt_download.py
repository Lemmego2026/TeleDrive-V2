import os
import sys
import json
import requests
import yt_dlp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

FILE_URL = os.environ.get("FILE_URL")
TG_BOT = os.environ.get("TELEGRAM_BOT_TOKEN")
TG_CHAT = os.environ.get("TELEGRAM_CHAT_ID")
GDRIVE_JSON = os.environ.get("GDRIVE_CREDENTIALS")
FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

def send_tg(msg):
    url = f"https://api.telegram.org/bot{TG_BOT}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHAT, "text": msg})

def main():
    if not FILE_URL:
        sys.exit(1)
    
    send_tg("⏳ در حال استخراج و دانلود با موتور yt-dlp...")
    file_path = None
    
    try:
        # تنظیمات yt-dlp برای دریافت بهترین کیفیت و نام‌گذاری استاندارد
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'restrictfilenames': True,
            'quiet': False
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(FILE_URL, download=True)
            file_path = ydl.prepare_filename(info_dict)
        
        filename = os.path.basename(file_path)
        send_tg(f"📦 استخراج تمام شد: `{filename}`\nدر حال انتقال به درایو...")

        creds = Credentials.from_authorized_user_info(
            json.loads(GDRIVE_JSON), 
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        service = build("drive", "v3", credentials=creds, cache_discovery=False)

        file_metadata = {"name": filename, "parents": [FOLDER_ID]}
        media = MediaFileUpload(file_path, resumable=False) 
        
        drive_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields="webViewLink",
            supportsAllDrives=True
        ).execute()

        send_tg(f"✅ فایل (توسط yt-dlp) آپلود شد!\n🔗 لینک مشاهده:\n{drive_file.get('webViewLink')}")

    except Exception as e:
        send_tg(f"❌ خطا در عملیات yt-dlp:\n`{str(e)}`")
        sys.exit(1)
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    main()
