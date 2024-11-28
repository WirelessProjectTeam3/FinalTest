import serial
import time

# 시리얼 포트 설정 (아두이노가 연결된 포트로 변경)
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # 시리얼 초기화 대기

# 졸음운전 판단 기준 설정
LOW_HEART_RATE = 50      # 낮은 심박수 임계값
CONSISTENT_THRESHOLD = 5  # 변동 폭이 작다고 판단할 심박수 차이
CHECK_INTERVAL = 10       # 검사 주기 (초)
WARNING_COUNT = 3         # 연속 경고 발생 횟수 기준

# 심박수 데이터 저장
heart_rate_data = []
warning_counter = 0

def check_drowsiness(heart_rate_data):
    global warning_counter

    if len(heart_rate_data) < 2:
        return False  # 데이터가 충분하지 않으면 판단하지 않음

    # 평균 심박수 계산
    avg_heart_rate = sum(heart_rate_data) / len(heart_rate_data)

    # 심박수가 임계값 이하인지 확인
    if avg_heart_rate < LOW_HEART_RATE:
        warning_counter += 1
        print(f"경고: 심박수 낮음! 평균 심박수: {avg_heart_rate:.2f}")
    else:
        warning_counter = 0

    # 변동 폭이 작아 일정한 상태인지 확인
    max_hr = max(heart_rate_data)
    min_hr = min(heart_rate_data)
    if max_hr - min_hr < CONSISTENT_THRESHOLD:
        warning_counter += 1
        print("경고: 심박수 변동 없음!")

    # 연속 경고 발생 시 졸음 판단
    if warning_counter >= WARNING_COUNT:
        print("졸음운전 감지! 알림을 전송합니다.")
        warning_counter = 0
        return True

    return False

try:
    while True:
        # 심박수 데이터 읽기
        data = ser.readline().decode('utf-8').strip()
        try:
            heart_rate = int(data)
            print(f"현재 심박수: {heart_rate}")
            heart_rate_data.append(heart_rate)

            # 일정 시간마다 검사
            if len(heart_rate_data) >= CHECK_INTERVAL:
                drowsy = check_drowsiness(heart_rate_data)
                if drowsy:
                    print("경고: 졸음운전 상태!")
                heart_rate_data = []  # 데이터 초기화
        except ValueError:
            print("유효하지 않은 데이터:", data)
except KeyboardInterrupt:
    print("프로그램 종료")
finally:
    ser.close()
