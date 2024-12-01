from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 가져오기
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 출력
if TELEGRAM_BOT_TOKEN:
    print(f"Loaded TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
else:
    print("TELEGRAM_BOT_TOKEN is not defined or failed to load.")

if TELEGRAM_CHAT_ID:
    print(f"Loaded TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
else:
    print("TELEGRAM_CHAT_ID is not defined or failed to load.")
