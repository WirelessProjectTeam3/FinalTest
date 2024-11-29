import threading
import serial
import cv2
import dlib
import imutils
from imutils import face_utils
from scipy.spatial import distance as dist
import tos
import datetime
import pyttsx3

# ============================
# 심박수 모듈
# ============================
def heart_rate_monitor(port="COM3", baud_rate=9600, threshold=10):
    ser = serial.Serial(port, baud_rate)
    heart_rate_history = []

    while True:
        if ser.in_waiting > 0:
            heart_rate = int(ser.readline().decode('utf-8').strip())
            heart_rate_history.append(heart_rate)
            if len(heart_rate_history) > 10:
                heart_rate_history.pop(0)
            
            avg_heart_rate = sum(heart_rate_history) / len(heart_rate_history)
            print(f"심장 박동 수: {heart_rate} bpm, 평균: {avg_heart_rate:.2f} bpm")

            if heart_rate < (avg_heart_rate - threshold):
                print("졸음 경고: 심박수가 평균보다 낮습니다!")

# ============================
# 얼굴 졸음 감지 모듈
# ============================
def drowsiness_detection():
    FACIAL_LANDMARK_PREDICTOR = "shape_predictor_68_face_landmarks.dat"
    EAR_THRESHOLD = 0.2
    ALARM_EAR_FRAMES = 5

    face_detector = dlib.get_frontal_face_detector()
    landmark_predictor = dlib.shape_predictor(FACIAL_LANDMARK_PREDICTOR)
    (leftEyeStart, leftEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rightEyeStart, rightEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    webcam_feed = cv2.VideoCapture(0)

    while True:
        status, frame = webcam_feed.read()
        if not status:
            print("웹캠 오류")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector(gray_frame, 0)

        for face in faces:
            landmarks = landmark_predictor(gray_frame, face)
            landmarks = face_utils.shape_to_np(landmarks)

            left_eye = landmarks[leftEyeStart:leftEyeEnd]
            right_eye = landmarks[rightEyeStart:rightEyeEnd]
            ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

            if ear < EAR_THRESHOLD:
                print("졸음 운전 경고!")
                cv2.putText(frame, "DROWSY DRIVING DETECTED!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        cv2.imshow("Drowsiness Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    webcam_feed.release()
    cv2.destroyAllWindows()

# EAR 계산 함수
def eye_aspect_ratio(eye):
    p2_p6 = dist.euclidean(eye[1], eye[5])
    p3_p5 = dist.euclidean(eye[2], eye[4])
    p1_p4 = dist.euclidean(eye[0], eye[3])
    return (p2_p6 + p3_p5) / (2.0 * p1_p4)

# ============================
# CO₂ 농도 모니터링 모듈
# ============================
def co2_monitor():
    CO2_THRESHOLD = 1000
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)

    def play_warning_message():
        engine.say("경고: CO2 농도가 임계값을 초과했습니다. 즉시 환기가 필요합니다.")
        engine.runAndWait()

    try:
        am = tos.AM()
        while True:
            p = am.read()
            if p:
                msg = OscilloscopeMsg(p.data)
                if msg.type == 1:
                    CO2 = 1.5 * msg.Data0 / 4096 * 2 * 1000
                    print(f"{datetime.datetime.now()} - CO2: {CO2:.2f} ppm")

                    if CO2 > CO2_THRESHOLD:
                        print("경고: CO2 농도가 임계값을 초과했습니다!")
                        play_warning_message()
    except Exception as e:
        print(f"오류 발생: {e}")

# ============================
# 메인 통합 시스템
# ============================
if __name__ == "__main__":
    heart_thread = threading.Thread(target=heart_rate_monitor, args=("COM3", 9600))
    drowsiness_thread = threading.Thread(target=drowsiness_detection)
    co2_thread = threading.Thread(target=co2_monitor)

    heart_thread.start()
    drowsiness_thread.start()
    co2_thread.start()

    heart_thread.join()
    drowsiness_thread.join()
    co2_thread.join()
