import cv2
import dlib
import imutils
from imutils import face_utils
from scipy.spatial import distance as dist
import pyttsx3  # 음성 합성 라이브러리

# EAR 계산 함수 정의
def eye_aspect_ratio(eye):
    p2_minus_p6 = dist.euclidean(eye[1], eye[5])  # 눈의 위아래 간격
    p3_minus_p5 = dist.euclidean(eye[2], eye[4])  # 눈의 좌우 간격
    p1_minus_p4 = dist.euclidean(eye[0], eye[3])  # 눈의 가로 길이
    return (p2_minus_p6 + p3_minus_p5) / (2.0 * p1_minus_p4)

# 음성 엔진 초기화
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # 음성 속도 설정
engine.setProperty('voice', 'Korean')  # 한국어 음성 설정 (OS에 따라 다를 수 있음)

# 초기 설정
FACIAL_LANDMARK_PREDICTOR = "shape_predictor_68_face_landmarks.dat"
MAXIMUM_FRAME_COUNT = 10
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor(FACIAL_LANDMARK_PREDICTOR)
(leftEyeStart, leftEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rightEyeStart, rightEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# 동적 EAR 임계값 설정을 위한 변수
ear_sum = 0
frame_count = 0
ear_threshold = 0.2
ear_alarm_flag = 0
ALARM_EAR_FRAMES = 5
SLEEP_DETECTED_FLAG = 0
voice_alert_flag = False  # 음성 알림 중복 방지 플래그

# 웹캠 시작
webcam_feed = cv2.VideoCapture(0)
print("Starting webcam...")

# 얼굴 랜드마크 및 EAR 계산 처리 함수
def process_frame(frame):
    global ear_sum, frame_count, ear_threshold, ear_alarm_flag, SLEEP_DETECTED_FLAG, voice_alert_flag

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
        ear_sum += ear

        if frame_count < MAXIMUM_FRAME_COUNT:
            frame_count += 1
            if frame_count == MAXIMUM_FRAME_COUNT:
                ear_threshold = (ear_sum / frame_count) * 0.8
                print(f"EAR Threshold dynamically set to: {ear_threshold:.2f}")
        else:
            if ear < ear_threshold:
                ear_alarm_flag += 1
            else:
                ear_alarm_flag = 0

        if ear_alarm_flag >= ALARM_EAR_FRAMES:
            SLEEP_DETECTED_FLAG = 1
        else:
            SLEEP_DETECTED_FLAG = 0

        if SLEEP_DETECTED_FLAG == 1:
            cv2.putText(frame, "DROWSY DRIVING DETECTED!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            if not voice_alert_flag:  # 중복 음성 알림 방지
                engine.say("졸음 운전이 의심됩니다!")
                engine.runAndWait()
                voice_alert_flag = True
        else:
            voice_alert_flag = False

        left_eye_hull = cv2.convexHull(left_eye)
        right_eye_hull = cv2.convexHull(right_eye)
        cv2.drawContours(frame, [left_eye_hull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [right_eye_hull], -1, (0, 255, 0), 1)

        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"EAR Threshold: {ear_threshold:.2f}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return frame

# 메인 루프
try:
    while True:
        status, frame = webcam_feed.read()
        if not status:
            print("웹캠에서 프레임을 읽을 수 없습니다.")
            break

        frame = imutils.resize(frame, width=800)
        processed_frame = process_frame(frame)

        cv2.imshow("Drowsiness Detection", processed_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"오류 발생: {e}")

finally:
    webcam_feed.release()
    cv2.destroyAllWindows()
