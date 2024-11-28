import cv2  # OpenCV: 컴퓨터 비전 라이브러리
import dlib  # 얼굴 검출 및 랜드마크 추출용 라이브러리
import imutils  # 이미지 처리 유틸리티 라이브러리
from imutils import face_utils  # dlib 랜드마크 데이터를 Numpy 배열로 변환하는 유틸리티
from scipy.spatial import distance as dist  # 두 점 간의 거리 계산을 위한 함수

# EAR(Eye Aspect Ratio) 계산 함수
def eye_aspect_ratio(eye):
    """
    눈의 랜드마크 좌표를 입력으로 받아 EAR을 계산.
    EAR = (p2-p6 거리 + p3-p5 거리) / (2 * p1-p4 거리)
    """
    p2_minus_p6 = dist.euclidean(eye[1], eye[5])  # 수직 거리 1
    p3_minus_p5 = dist.euclidean(eye[2], eye[4])  # 수직 거리 2
    p1_minus_p4 = dist.euclidean(eye[0], eye[3])  # 수평 거리
    ear = (p2_minus_p6 + p3_minus_p5) / (2.0 * p1_minus_p4)
    return ear

# 상수 및 변수 초기화
FACIAL_LANDMARK_PREDICTOR = "shape_predictor_68_face_landmarks.dat"  # 랜드마크 모델 파일 경로
MINIMUM_EAR = 0.2  # EAR 임계값 (0.2 이하면 졸음으로 간주)
MAXIMUM_FRAME_COUNT = 10  # EAR이 지속되는 최대 프레임 수
MINIMUM_HEAD_POSITION_Y = 30  # 머리 위치가 낮아졌다고 판단하는 픽셀 값 차이
HEAD_POSITION_CHECK_FRAMES = 10  # 머리 위치를 평가할 프레임 수

# dlib 객체 초기화
faceDetector = dlib.get_frontal_face_detector()  # dlib 얼굴 검출기
landmarkFinder = dlib.shape_predictor(FACIAL_LANDMARK_PREDICTOR)  # 랜드마크 모델 로드

# 웹캠 피드 가져오기
webcamFeed = cv2.VideoCapture(0)  # 기본 웹캠 사용

# 랜드마크 인덱스 가져오기
(leftEyeStart, leftEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]  # 왼쪽 눈
(rightEyeStart, rightEyeEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]  # 오른쪽 눈
(noseStart, noseEnd) = face_utils.FACIAL_LANDMARKS_IDXS["nose"]  # 코

# 졸음 감지 카운터 및 머리 위치 초기화
EYE_CLOSED_COUNTER = 0
head_position_y_values = []  # 머리 높이를 저장할 리스트

try:
    while True:  # 무한 루프를 통해 실시간 처리
        (status, image) = webcamFeed.read()  # 웹캠에서 프레임 읽기
        if not status:
            break  # 프레임을 읽을 수 없으면 종료

        # 이미지 크기 조정
        image = imutils.resize(image, width=800)  # 화면 너비를 800픽셀로 고정

        # 이미지 회색조 변환
        grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 얼굴 검출
        faces = faceDetector(grayImage, 0)

        for face in faces:  # 감지된 각 얼굴에 대해
            # 얼굴 랜드마크 추출
            faceLandmarks = landmarkFinder(grayImage, face)
            faceLandmarks = face_utils.shape_to_np(faceLandmarks)

            # 왼쪽, 오른쪽 눈 좌표 가져오기
            leftEye = faceLandmarks[leftEyeStart:leftEyeEnd]
            rightEye = faceLandmarks[rightEyeStart:rightEyeEnd]

            # EAR 계산
            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0  # 왼쪽 눈과 오른쪽 눈의 EAR 평균

            # 눈 윤곽선을 화면에 그리기
            leftEyeHull = cv2.convexHull(leftEye)  # 왼쪽 눈 윤곽
            rightEyeHull = cv2.convexHull(rightEye)  # 오른쪽 눈 윤곽
            cv2.drawContours(image, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(image, [rightEyeHull], -1, (0, 255, 0), 1)

            # 머리 중심 위치 계산 (얼굴의 중앙 Y값 사용)
            head_position_y = (face.top() + face.bottom()) // 2
            head_position_y_values.append(head_position_y)

            # 최근 프레임에서 머리 위치 변화 분석
            if len(head_position_y_values) > HEAD_POSITION_CHECK_FRAMES:
                head_position_y_values.pop(0)
                avg_head_position_y = sum(head_position_y_values) / len(head_position_y_values)
                head_position_delta = abs(head_position_y - avg_head_position_y)

                if head_position_delta > MINIMUM_HEAD_POSITION_Y:  # 머리가 낮아졌는지 체크
                    cv2.putText(image, "Warning! Head Drooping!", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # EAR 임계값 체크
            if ear < MINIMUM_EAR:
                EYE_CLOSED_COUNTER += 1  # 눈 감은 상태 지속 카운트
            else:
                EYE_CLOSED_COUNTER = 0  # 눈을 뜨면 카운터 초기화

            # EAR 값 출력
            cv2.putText(image, f"EAR: {round(ear, 2)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # 졸음 경고
            if EYE_CLOSED_COUNTER >= MAXIMUM_FRAME_COUNT:  # 눈 감은 상태가 일정 시간 이상 지속되면
                cv2.putText(image, "Warning! Eyes Closed!", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # 최종 프레임 화면에 출력
        cv2.imshow("Frame", image)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q'를 누르면 종료
            break

except Exception as e:
    print(f"Error! : {e}")

finally:
    webcamFeed.release()  # 웹캠 리소스 해제
    cv2.destroyAllWindows()  # 모든 창 닫기
