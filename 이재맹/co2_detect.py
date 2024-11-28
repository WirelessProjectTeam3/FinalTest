#파일 실행 명령어 python co2_detect.py(파일명) serial@dev/ttyUSB0:115200

import sys  # 시스템 명령어를 다루기 위한 모듈
import tos  # TinyOS와 시리얼 통신을 위한 모듈
import datetime  # 현재 날짜와 시간을 가져오기 위한 모듈
import pyttsx3  # 음성 합성을 위한 모듈

# CO2 임계값 설정 (ppm 기준)
CO2_THRESHOLD = 1000    #테스트할 때 스피커 출력이 재대로 되는지 확인하기 위해 임의로 다른 숫자로 바꿔도 됩니다.

# pyttsx3 음성 엔진 초기화
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # 음성 속도 설정
engine.setProperty('voice', 'Korean')  # 목소리 설정(한국어로 설정)

# TinyOS 패킷을 처리하기 위한 클래스 정의
class OscilloscopeMsg(tos.Packet):
    def __init__(self, packet=None):
        # 패킷 포맷을 정의: 각 필드는 데이터 타입과 크기(바이트)로 정의됨
        tos.Packet.__init__(self,
                            [('srcID', 'int', 2),   # 송신기 ID
                             ('seqNo', 'int', 4),   # 시퀀스 번호
                             ('type', 'int', 2),    # 데이터 타입 (예: CO2, 온도 등)
                             ('Data0', 'int', 2),   # 데이터 값 0 (주로 CO2 데이터)
                             ('Data1', 'int', 2),   # 데이터 값 1 (추가 센서 데이터)
                             ('Data2', 'int', 2),   # 데이터 값 2 (추가 센서 데이터)
                             ('Data3', 'int', 2),   # 데이터 값 3
                             ('Data4', 'int', 2),   # 데이터 값 4
                             ('Data5', 'int', 2)],  # 데이터 값 5
                            packet)

# 명령어 도움말 출력 (인자 '-h'가 주어진 경우)
if '-h' in sys.argv:
    print("Usage:", sys.argv[0], "serial@/dev/ttyUSB0:57600")
    sys.exit()

# AM 객체 생성 (시리얼 포트 통신 설정)
try:
    am = tos.AM()  # 기본 인자 없으면 자동으로 설정됨
    print("AM 객체가 생성되었습니다.")
except Exception as e:
    print("AM 객체 생성 오류:", e)
    sys.exit(1)

print("데이터 수신을 시작합니다...")

# 데이터 수신 루프
while True:
    try:
        p = am.read()  # 패킷 읽기
        if p:
            # 읽은 패킷 데이터를 OscilloscopeMsg 형식으로 변환
            msg = OscilloscopeMsg(p.data)
            if msg.type == 1:  # CO2 데이터 타입 확인
                CO2 = msg.Data0  # CO2 데이터 추출
                CO2 = 1.5 * CO2 / 4096 * 2 * 1000  # 데이터 변환 (ppm 기준)
                print(f"{datetime.datetime.now()} - CO2: {CO2:.2f} ppm")   #화면에 지금 시간하고 이산화탄소 농도 출력

                # CO2 농도가 임계값 초과 시 경고 메시지 출력 및 음성 알림
                if CO2 > CO2_THRESHOLD:
                    print("경고: CO₂ 농도가 임계값을 초과했습니다! 즉시 환기가 필요합니다!")
                    engine.say("이산화탄소 농도가 높습니다. 즉시 환기가 필요합니다.")
                    engine.runAndWait()  # 음성 출력 실행
    except KeyboardInterrupt:
        # 키보드 인터럽트로 프로그램 종료 시 출력
        print("프로그램이 종료되었습니다.")
        break
    except Exception as e:
        # 기타 예외 발생 시 출력
        print(f"오류 발생: {e}")
        break
