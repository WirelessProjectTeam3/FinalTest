import serial
import time

# 아두이노가 연결된 시리얼 포트 설정
arduino_port = "COM3"
baud_rate = 9600

# 시리얼 포트 열기
ser = serial.Serial(arduino_port, baud_rate)
time.sleep(2)

print("연결 시작")

# 심박수 기록을 위한 변수
heart_rate_history = []
warning_threshold = 10  # 평균 심박수보다 10 bpm 이상 낮을 때 경고
check_duration = 5  # 5초 동안 낮은 심박수가 유지되면 졸음 경고

try:
    while True:
        # 시리얼 데이터 읽기
        if ser.in_waiting > 0:
            heart_rate = ser.readline().decode('utf-8').strip()
            print(heart_rate)
            heart_rate_history.append(heart_rate)

            # 최근 10초 동안의 심박수 기록을 유지
            if len(heart_rate_history) > 10:
                heart_rate_history.pop(0)

            # 평균 심박수 계산
            avg_heart_rate = sum(heart_rate_history) / len(heart_rate_history)

            print(f"심장 박동 수: {heart_rate} bpm, 평균: {avg_heart_rate:.2f} bpm")

            # 졸음 상태 감지
            if heart_rate < (avg_heart_rate - warning_threshold):
                print("졸음 경고: 심박수가 평균보다 낮습니다!")

        time.sleep(1)

except KeyboardInterrupt:
    print("연결 중단")
finally:
    ser.close()