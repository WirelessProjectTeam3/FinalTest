from dotenv import load_dotenv
import auth
import requests
import os

load_dotenv() # .env 파일 로드

SMS_API_KEY = os.environ.get("SMS_API_KEY")
SMS_API_SECRET = os.environ.get("SMS_API_SECRET")
SMS_FROM_PHONE_NUMBER =os.environ.get("SMS_FROM_PHONE_NUMBER")

# API에 메시지 전송 요청
def send(to_phone_number):
    params = dict()
    params["message"] = dict()
    params["message"]["to"] = to_phone_number # 받는 사람 번호
    params["message"]["from"] = SMS_FROM_PHONE_NUMBER # 보내는 사람 번호
    params["message"]["text"] = "test" # 내용
    
    res = requests.post("https://api.solapi.com/messages/v4/send",
                        headers=auth.get_headers(SMS_API_KEY, SMS_API_SECRET),
                        json=params)
    
    if res.status_code == 200:
        print("전송 완료")
    else:
        print("전송 실패")

    