# SMS 서비스 및 전화번호 관리 봇

**쿨에스엠에스(CoolSMS)** API를 사용하여 SMS를 보내고, **Telegram Bot**을 사용하여 전화번호를 등록하고 조회할 수 있는 기능 구현

## 기능

### 1. **SMS 서비스 (`send_sms.py`)**

쿨에스엠에스 API를 이용하여 등록된 수신자에게 SMS 메시지를 전송하는 기능을 제공합니다.

- **환경 변수**:
  - `SMS_API_KEY`: 쿨에스엠에스 API 키
  - `SMS_API_SECRET`: 쿨에스엠에스 API 시크릿 키
  - `SMS_FROM_PHONE_NUMBER`: 발신자 전화번호
- **핵심 기능**:
  - 특정 수신자 번호로 SMS 메시지 전송
  - API 요청을 위한 인증 헤더 생성
  - SMS 전송 성공/실패 여부를 확인하는 응답 처리

### 2. **전화번호 등록 및 조회 봇 (`bot.py`)**

Telegram 봇을 통해 전화번호를 등록하고, 저장된 전화번호를 조회할 수 있는 기능을 제공합니다.
봇 이름 : PDD_Setting_bot(Prevent drowsy driving)

- **환경 변수**:
  - `TELEGRAM_TOKEN`: Telegram 봇 토큰
  - `TELEGRAM_CHAT_ID`: 사용자 chat_id
- **핵심 기능**:
  - `/set <전화번호>`: 010으로 시작하는 11자리 전화번호 등록
  - `/get`: 등록된 전화번호 조회
  - 특정 chat_id만 사용 가능하도록 인증 기능 추가
  - 봇 시작 시 사용 방법 안내 메시지 전송

## 라이브러리 설치 및 .env 파일

### 라이브러리 설치

```
pip install requests
pip install python-telegram-bot
pip install python-dotenv
```

### .env 파일

```
SMS_API_KEY = '쿨에스엠에스에서 발급 받은 API KEY'
SMS_API_SECRET = '쿨에스엠에스에서 발급 받은 SECRET API KEY'
SMS_FROM_PHONE_NUMBER = '쿨에스엠에스에 인증된 발신자 번호'
TELEGRAM_TOKEN = '텔레그램 봇 토큰'
TELEGRAM_CHAT_ID = '텔레그램 챗 아이디'
```

## 사용 예시

### SMS 기능
<img src="https://github.com/user-attachments/assets/28437a46-55fa-4ad2-b821-dc4b0ab82aea"  width="300" height="500"/>
<img src="https://github.com/user-attachments/assets/cb7627d9-bd9b-4e29-9646-fdd9fa175ac7"  width="300" height="500"/>

### 텔레그램 봇
<img src="https://github.com/user-attachments/assets/83305753-997b-49d0-bbf4-81ebb40b486b"  width="300" height="500"/>
<img src="https://github.com/user-attachments/assets/e2bc22e4-f18a-4aae-8d12-e798c1969259"  width="300" height="500"/>
<img src="https://github.com/user-attachments/assets/5d5b3e0a-b129-4d87-b15d-c31fd250d1e7"  width="300" height="500"/>

## 참조
[https://github.com/coolsms/coolsms-python](https://github.com/coolsms/coolsms-python)

[https://docs.coolsms.co.kr/api-reference/messages/sendsimplemessage#body-params](https://docs.coolsms.co.kr/api-reference/messages/sendsimplemessage#body-params)

[https://core.telegram.org/bots/api](https://core.telegram.org/bots/api)
