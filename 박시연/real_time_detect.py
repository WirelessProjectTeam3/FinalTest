import cv2
import dlib
import imutils
from imutils import face_utils
from scipy.spatial import distance as dist

# EAR 계산 함수 정의: 눈의 비율을 계산하는 함수입니다.
def eye_aspect_ratio(eye):
    # p2-p6, p3-p5, p1-p4 간의 거리 계산 (눈의 형태를 계산하기 위해)
    p2_minus_p6 = dist.euclidean(eye[1], eye[5])  # 눈의 위아래 간격
    p3_minus_p5 = dist.euclidean(eye[2], eye[4])  # 눈의 좌우 간격
    p1_minus_p4 = dist.euclidean(eye[0], eye[3])  # 눈의 가로 길이
    # EAR 계산: (수직 거리 합) / (수평 거리)
    ear = (p2_minus_p6 + p3_minus_p5) / (2.0 * p1_minus_p4)
    return ear  # EAR 값 반환

# 초기 설정
FACIAL_LANDMARK_PREDICTOR = "shape_predictor_68_face_landmarks.dat"  # 얼굴 랜드마크 예측 파일 경로
MAXIMUM_FRAME_COUNT = 10  # EAR 임계값 설정을 위한 초기 프레임 수
face_detector = dlib.get_frontal_face_detector()  # 얼굴 검출기 초기화
landmark_predictor = dlib.shape_predictor(FACIAL_LANDMARK_PREDICTOR)  # 랜드마크 예측기 초기화
(leftEyeStart, leftEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]  # 왼쪽 눈의 랜드마크 인덱스
(rightEyeStart, rightEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]  # 오른쪽 눈의 랜드마크 인덱스

# 동적 EAR 임계값 설정을 위한 변수
ear_sum = 0  # EAR 값의 누적 합
frame_count = 0  # 처리된 프레임 수
ear_threshold = 0.2  # 초기 EAR 임계값 설정
ear_alarm_flag = 0  # EAR 임계값을 초과한 횟수 (알람을 위한 플래그)
ALARM_EAR_FRAMES = 5  # EAR 값이 연속으로 5프레임 이하일 경우 졸음운전 감지
SLEEP_DETECTED_FLAG = 0  # 졸음운전 감지 여부 플래그 (0: 감지 안 됨, 1: 감지 됨)

# 웹캠 시작
webcam_feed = cv2.VideoCapture(0)  # 웹캠 피드를 가져옴
print("Starting webcam...")  # 웹캠 시작 알림 출력

# 얼굴 랜드마크 및 EAR 계산 처리 함수
def process_frame(frame):
    global ear_sum, frame_count, ear_threshold, ear_alarm_flag, SLEEP_DETECTED_FLAG

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 프레임을 그레이스케일로 변환
    faces = face_detector(gray_frame, 0)  # 얼굴 검출

    for face in faces:
        landmarks = landmark_predictor(gray_frame, face)  # 얼굴에서 랜드마크 추출
        landmarks = face_utils.shape_to_np(landmarks)  # numpy 배열로 변환

        # 왼쪽과 오른쪽 눈의 EAR 계산
        left_eye = landmarks[leftEyeStart:leftEyeEnd]  # 왼쪽 눈
        right_eye = landmarks[rightEyeStart:rightEyeEnd]  # 오른쪽 눈
        left_ear = eye_aspect_ratio(left_eye)  # 왼쪽 눈 EAR 계산
        right_ear = eye_aspect_ratio(right_eye)  # 오른쪽 눈 EAR 계산
        ear = (left_ear + right_ear) / 2.0  # 전체 EAR 값 계산
        ear_sum += ear  # 누적 EAR 값에 추가

        # 동적 EAR 임계값 설정 (초기 10 프레임 기준)
        if frame_count < MAXIMUM_FRAME_COUNT:
            frame_count += 1
            if frame_count == MAXIMUM_FRAME_COUNT:
                # 평균 EAR 값의 80%를 EAR 임계값으로 설정
                ear_threshold = (ear_sum / frame_count) * 0.8
                print(f"EAR Threshold dynamically set to: {ear_threshold:.2f}")
        else:
            # EAR 값이 동적 임계값보다 작은 경우 알람 플래그 증가
            if ear < ear_threshold:
                ear_alarm_flag += 1
            else:
                ear_alarm_flag = 0  # EAR 값이 임계값을 초과하면 알람 플래그 초기화

        # 졸음운전 감지: EAR 값이 연속으로 낮으면 졸음운전으로 감지
        if ear_alarm_flag >= ALARM_EAR_FRAMES:
            SLEEP_DETECTED_FLAG = 1  # 졸음운전 감지
        else:
            SLEEP_DETECTED_FLAG = 0  # 졸음운전 미감지

        # 졸음운전 감지 알림 출력
        if SLEEP_DETECTED_FLAG == 1:
            cv2.putText(frame, "DROWSY DRIVING DETECTED!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

        # 눈 윤곽선 그리기 (시각적으로 눈을 강조하기 위해 윤곽선 추가)
        left_eye_hull = cv2.convexHull(left_eye)
        right_eye_hull = cv2.convexHull(right_eye)
        cv2.drawContours(frame, [left_eye_hull], -1, (0, 255, 0), 1)  # 왼쪽 눈의 윤곽선 그리기
        cv2.drawContours(frame, [right_eye_hull], -1, (0, 255, 0), 1)  # 오른쪽 눈의 윤곽선 그리기

        # 디버그 정보 출력 (EAR 값과 EAR 임계값을 화면에 표시)
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"EAR Threshold: {ear_threshold:.2f}", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    return frame  # 처리된 프레임 반환

# 메인 루프: 웹캠에서 계속해서 프레임을 읽고 처리하는 루프
try:
    while True:
        status, frame = webcam_feed.read()  # 웹캠에서 프레임 읽기
        if not status:  # 웹캠에서 프레임을 읽지 못하면 종료
            print("웹캠에서 프레임을 읽을 수 없습니다.")
            break

        frame = imutils.resize(frame, width=800)  # 프레임 크기 조정
        processed_frame = process_frame(frame)  # 프레임 처리

        # 처리된 프레임을 화면에 표시
        cv2.imshow("Drowsiness Detection", processed_frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"오류 발생: {e}")  # 예외 발생 시 출력

finally:
    webcam_feed.release()  # 웹캠 리소스 해제
    cv2.destroyAllWindows()  # 모든 창 종료
