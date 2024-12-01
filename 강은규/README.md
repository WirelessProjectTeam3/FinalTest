![image](https://github.com/user-attachments/assets/96defe3b-16a3-4afa-ade2-af1978147f37)
## 각각의 코드 분석
### co2_detect.py

##### 특징
- zigbee네트워크를 통해 데이터를 받음
- TinyOS 패킷을 처리함
##### 통합시 유의사항
- 라즈베리 파이의 전원을 재부팅하거나 USB를 뺐다 꽂을 경우 tty/USB포트를 제대로 찾지 못함
	- 동적으로 포트를 할당하여 해결함

### heartbeat_detect.py

##### 특징
- 아두이노를 통해 시리얼 데이터를 받음
- 실시간으로 심박수의 평균값을 구해 현재의 심박수와 비교함
##### 통합시 유의사항
- 기기 이슈로 인해 제대로된 값을 찾지 못 함 
	- 초안 작성시 mock데이터 삽입하여 테스트

### real_time_detect.py

##### 특징
- 카메라를 이용해 실시간으로 눈의 개폐상태를 체크

##### 통합시 유의사항
- shape_predictor_68_face_landmarks.dat가 있어야지 실행 가능


### send_sms.py

##### 특징
- API발급 필요


### telegram_bot.py
##### 특징
- 봇 생성 및 토큰 발급 필요


## 통합

### 초안 작성
- 각각의 코드를 함수로 만들어 사용
	- 모듈화를 선택시 난이도가 더 높다고 판단

- 각 함수는 병렬적으로 돌아가야함

### 통합코드 tel_summary.py 작성

- 텔레그램을 이용하여 전화번호 세팅, 수집한 데이터 모니터링, 시스템 종료가 가능하게 구현

- 소스 코드
```
import threading
import time
from queue import Queue
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import cv2
import dlib
import imutils
from imutils import face_utils
from scipy.spatial import distance as dist
import pyttsx3  # pyttsx3 라이브러리 import 추가
import auth  # 인증 모듈 추가
import serial
import asyncio

# 환경 변수 로드
load_dotenv()

# 텔레그램 및 SMS 설정
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SMS_API_KEY = "NCSCCGGEU7GMJBJH"
SMS_API_SECRET = "QQXSK847HW1LEONHHWYFVA1J3QJQZVOX"
SMS_FROM_PHONE_NUMBER = "01068659647"
saved_phone_number = None  # set 명령으로 설정된 전화번호 저장

# 시스템 전역 변수
system_running = True
queue = Queue()
heart_rate_history = []
co2_data_history = []

# 아두이노 포트 설정
arduino_port = "/dev/ttyACM0"  # 라즈베리 파이의 시리얼 포트 설정
baud_rate = 9600

# 시리얼 포트 열기
ser = None
try:
    ser = serial.Serial(arduino_port, baud_rate)
    time.sleep(2)
    print("아두이노와 연결 성공")
except serial.SerialException as e:
    print(f"아두이노 연결 실패: {e}")

# CO2 센서 포트 설정
co2_serial = None
try:
    co2_serial = serial.Serial("/dev/ttyUSB0", 115200)
    print("CO2 센서 연결 성공")
except serial.SerialException as e:
    print(f"CO2 센서 연결 실패: {e}")

# CO2 센서 연결 실패 시 오류 처리
def validate_serial_connection(serial_obj, name):
    if serial_obj is None:
        print(f"{name} 연결이 실패했습니다. 연결 확인 후 재시도하십시오.")
        return False
    return True

if not validate_serial_connection(co2_serial, "CO2 센서"):
    system_running = False
if not validate_serial_connection(ser, "아두이노"):
    system_running = False

# pyttsx3 음성 엔진 초기화 (전역적으로 생성하여 재사용)
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # 음성 속도 설정
engine.setProperty('voice', 'Korean')  # 목소리 설정 (한국어로 설정)

# 패킷을 처리하기 위한 클래스 정의
class OscilloscopeMsg:
    def __init__(self, packet):
        self.srcID = int.from_bytes(packet[0:2], 'big')
        self.seqNo = int.from_bytes(packet[2:6], 'big')
        self.type = int.from_bytes(packet[6:8], 'big')
        self.data = int.from_bytes(packet[8:10], 'big')

# CO2 데이터 처리 함수
def co2_monitor():
    global system_running, co2_serial, queue
    while system_running:
        if co2_serial is None:
            print("CO2 센서가 연결되지 않았습니다. 모니터링을 건너뜁니다.")
            return
        try:
            if co2_serial.in_waiting > 0:
                packet = co2_serial.read(10)
                msg = OscilloscopeMsg(packet)
                if msg.type == 1:  # CO2 데이터 타입 확인
                    co2_value = 1.5 * msg.data / 4096 * 2 * 1000  # 데이터 변환 (ppm 기준)
                    co2_data_history.append(co2_value)
                    queue.put(co2_value)
                    print(f"CO2: {co2_value:.2f} ppm")
        except Exception as e:
            print(f"CO2 감지 오류: {e}")

# SMS 전송 함수
def send_sms(to_phone_number):
    params = {
        "message": {
            "to": to_phone_number,
            "from": SMS_FROM_PHONE_NUMBER,
            "text": "졸음 감지! 즉시 주의를 기울이세요."
        }
    }

    res = requests.post(
        "https://api.solapi.com/messages/v4/send",
        headers=auth.get_headers(SMS_API_KEY, SMS_API_SECRET),
        json=params
    )

    if res.status_code == 200:
        print(f"SMS 전송 완료: {to_phone_number}")
    else:
        print(f"SMS 전송 실패: {res.text}")

# EAR 계산 함수
def eye_aspect_ratio(eye):
    p2_minus_p6 = dist.euclidean(eye[1], eye[5])  # 위아래 간격
    p3_minus_p5 = dist.euclidean(eye[2], eye[4])  # 위아래 간격
    p1_minus_p4 = dist.euclidean(eye[0], eye[3])  # 좌우 간격
    ear = (p2_minus_p6 + p3_minus_p5) / (2.0 * p1_minus_p4)
    return ear

# 음성 알림 함수 정의
def voice_alert(message):
    global engine
    try:
        engine.say(message)
        engine.runAndWait()
    except Exception as e:
        print(f"음성 알림 오류: {e}")

# 졸음 감지 함수
def drowsiness_detection():
    global system_running, saved_phone_number

    FACIAL_LANDMARK_PREDICTOR = "shape_predictor_68_face_landmarks.dat"
    face_detector = dlib.get_frontal_face_detector()
    landmark_predictor = dlib.shape_predictor(FACIAL_LANDMARK_PREDICTOR)
    (leftEyeStart, leftEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rightEyeStart, rightEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    ear_threshold = 0.2
    alarm_frames = 5
    ear_alarm_flag = 0

    webcam_feed = cv2.VideoCapture(0)
    print("웹캠 시작...")

    while system_running:
        try:
            status, frame = webcam_feed.read()
            if not status:
                print("웹캠에서 프레임을 읽을 수 없습니다.")
                break

            frame = imutils.resize(frame, width=800)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector(gray_frame, 0)

            for face in faces:
                landmarks = landmark_predictor(gray_frame, face)
                landmarks = face_utils.shape_to_np(landmarks)

                left_eye = landmarks[leftEyeStart:leftEyeEnd]
                right_eye = landmarks[rightEyeStart:rightEyeEnd]
                left_ear = eye_aspect_ratio(left_eye)
                right_ear = eye_aspect_ratio(right_eye)
                ear = (left_ear + right_ear) / 2.0

                if ear < ear_threshold:
                    ear_alarm_flag += 1
                else:
                    ear_alarm_flag = 0

                if ear_alarm_flag >= alarm_frames:
                    alert = "졸음 감지! 즉시 주의를 기울이세요."
                    print(alert)
                    voice_alert(alert)  # 음성 알림 호출
                    if saved_phone_number:
                        send_sms(saved_phone_number)  # SMS 경고 전송

                cv2.putText(frame, f"EAR: {ear:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("Drowsiness Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"오류 발생: {e}")

    webcam_feed.release()
    cv2.destroyAllWindows()

# 심박수 감지 함수
def heartbeat_detection():
    global system_running, heart_rate_history

    warning_threshold = 10  # 평균 심박수보다 10 bpm 이상 낮을 때 경고

    if ser is None:
        print("아두이노 연결이 필요합니다. 심박수 감지를 건너뜁니다.")
        return

    while system_running:
        try:
            if ser.in_waiting > 0:
                raw_data = ser.readline().decode('utf-8').strip()
                try:
                    heart_rate = int(raw_data)
                    heart_rate_history.append(heart_rate)

                    if len(heart_rate_history) > 10:
                        heart_rate_history.pop(0)

                    avg_heart_rate = sum(heart_rate_history) / len(heart_rate_history)

                    print(f"심장 박동 수: {heart_rate} bpm, 평균: {avg_heart_rate:.2f} bpm")

                    if heart_rate < (avg_heart_rate - warning_threshold):
                        alert = "졸음 경고: 심박수가 평균보다 낮습니다!"
                        print(alert)
                        voice_alert(alert)  # 음성 알림 호출
                        if saved_phone_number:
                            send_sms(saved_phone_number)  # SMS 경고 전송
                except ValueError:
                    # 아두이노 초기 메시지나 잘못된 데이터가 수신될 경우 예외 처리
                    print(f"받은 데이터 무시: {raw_data}")

            time.sleep(1)

        except Exception as e:
            print(f"심박수 감지 오류: {e}")

# 텔레그램 명령어: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "시스템에 오신 것을 환영합니다. 사용 가능한 명령:\n"
        "/set <전화번호> - 전화번호 등록\n"
        "/monitor - 모니터링 데이터 확인\n"
        "/stop - 시스템 종료"
    )

# 텔레그램 명령어: /set
async def set_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global saved_phone_number
    if len(context.args) < 1:
        await update.message.reply_text("사용법: /set <전화번호>")
        return
    phone_number = context.args[0]
    if phone_number.startswith("010") and len(phone_number) == 11:
        saved_phone_number = phone_number
        await update.message.reply_text(f"전화번호 {phone_number}가 등록되었습니다.")
    else:
        await update.message.reply_text("유효하지 않은 전화번호입니다.")

# 텔레그램 명령어: /monitor
async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global heart_rate_history, co2_data_history
    if not heart_rate_history and not co2_data_history:
        await update.message.reply_text("현재 모니터링 데이터가 없습니다.")
    else:
        messages = []
        if heart_rate_history:
            avg_heart_rate = sum(heart_rate_history) / len(heart_rate_history)
            messages.append(f"최근 심박수: {heart_rate_history[-1]} bpm\n평균 심박수: {avg_heart_rate:.2f} bpm")
        if not queue.empty():
            while not queue.empty():
                co2_data = queue.get()
                co2_data_history.append(co2_data)
        if co2_data_history:
            messages.append(f"최근 CO2 데이터: {co2_data_history[-1]:.2f} ppm")
        response = "\n".join(messages)
        await update.message.reply_text(f"모니터링 데이터:\n{response}")

# 텔레그램 명령어: /stop
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global system_running
    system_running = False
    await update.message.reply_text("시스템이 종료됩니다.")

# 메인 함수 수정
def main():
    # 텔레그램 봇 설정
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("set", set_phone))
    app.add_handler(CommandHandler("monitor", monitor))
    app.add_handler(CommandHandler("stop", stop))

    # 센서 모니터링 스레드 시작
    sensor_threads = [
        threading.Thread(target=drowsiness_detection),  # 졸음 감지
        threading.Thread(target=heartbeat_detection),  # 심박수 감지
        threading.Thread(target=co2_monitor),  # CO2 감지
    ]
    for thread in sensor_threads:
        thread.start()

    # 텔레그램 봇 실행
    app.run_polling()

    # 모든 스레드 종료 대기
    for thread in sensor_threads:
        thread.join()

if __name__ == "__main__":
    main()
```

- 실행 화면(텔레그램)

![image](https://github.com/user-attachments/assets/f6bceefe-b991-4e48-8e0c-2eb1c240ac58)


- 실행 화면(SMS전송)

![image](https://github.com/user-attachments/assets/84d5e82d-818c-4a11-9491-a4c8a26132e2)

