from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os
import re

# 환경 변수 로드
load_dotenv()

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")  # 텔레그램 봇 토큰
TELEGRAM_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID"))  # 특정 chat_id

# 전화번호를 저장할 전역 변수
saved_phone_number = None

# 봇 시작 시 메시지 전송
async def send_start_message(update: Update):
    await update.bot.sendMessage(TELEGRAM_CHAT_ID, "안녕하세요. 졸음 운전 방시 시스템의 전화 번호 등록 봇입니다.\n" + 
                                                    "사용 방법\n" +
                                                    "/set <전화번호> - 전화번호 등록\n"+
                                                    "/get - 등록된 전화번호 확인")
                                                    
# 전화번호 등록 명령어
async def set_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    010으로 시작하고 총 11자리인 유효한 전화번호를 등록
    사용법: /set <전화번호>
    """
    global saved_phone_number

    # chat_id가 인증된 사용자인지 확인
    if update.effective_chat.id != TELEGRAM_CHAT_ID:
        await update.message.reply_text("이 봇을 사용할 권한이 없습니다.")
        return

    # 명령어에 아무 문자도 포함되지 않은 경우
    if len(context.args) < 1:
        await update.message.reply_text("사용법: /set <전화번호>")
        return

    phone_number = context.args[0]

    # 전화번호 형식 검증
    if re.fullmatch(r"010\d{8}", phone_number):
        saved_phone_number = phone_number
        await update.message.reply_text(f"전화번호 {phone_number}가 성공적으로 저장되었습니다!")
    else:
        await update.message.reply_text("유효하지 않은 전화번호입니다. 010으로 시작하는 11자리 숫자를 입력하세요.")

# 등록된 전화번호 가져오기 명령어
async def get_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    등록된 전화번호를 봇을 통해 전달
    사용법: /get
    """
    
    # chat_id가 인증된 사용자인지 확인
    if update.effective_chat.id != TELEGRAM_CHAT_ID:
        await update.message.reply_text("이 봇을 사용할 권한이 없습니다.")
        return

    if saved_phone_number:
        await update.message.reply_text(f"등록된 전화번호: {saved_phone_number}")
    else:
        await update.message.reply_text("등록된 전화번호가 없습니다.")

# 봇 실행 함수
def bot_start():
    """봇을 실행합니다."""
    application = Application.builder().token(TELEGRAM_TOKEN).post_init(send_start_message).build()
    
    # 명령어 핸들러 등록
    application.add_handler(CommandHandler("set", set_phone_number))
    application.add_handler(CommandHandler("get", get_phone_number))

    # 봇 실행
    application.run_polling()