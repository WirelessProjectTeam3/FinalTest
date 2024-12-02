# CO₂ 농도 측정 및 경고 시스템

이 프로젝트는 차량 내부의 CO₂ 농도를 실시간으로 모니터링하여 졸음 운전 위험성을 줄이고, 실내 공기질을 개선하기 위해 설계되었습니다. Zigbee 통신을 활용해 센서 데이터를 안정적으로 수집하며, Raspberry Pi를 통해 데이터를 처리하고 음성 경고를 제공합니다.

## 📋 주요 기능

- **이산화탄소 농도 측정**: 차량 내부의 CO₂ 농도를 실시간으로 감지하고, 임계값 초과 시 경고를 제공합니다.
- **음성 경고 시스템**: 설정된 임계값을 초과할 경우 음성 메시지를 통해 즉각적인 환기 알림을 제공합니다.
- **Zigbee 데이터 전송**: 센서 데이터를 Zigbee 통신을 통해 Raspberry Pi로 전송하여 안정적이고 효율적인 데이터 흐름을 보장합니다.
- **실시간 데이터 처리**: Raspberry Pi에서 데이터를 처리하여 CO₂ 농도가 위험 수준에 도달했는지 판단하고, 즉각 경고 메시지를 출력합니다.

## 📊 데이터 흐름

![데이터 흐름 다이어그램](https://github.com/user-attachments/assets/6dd596ab-ffda-4691-8f16-840387ed6b95)

1. **데이터 수집**: CO₂ 센서가 Zigbee 네트워크를 통해 데이터를 Raspberry Pi로 전송합니다.
2. **데이터 처리**: Raspberry Pi에서 수신한 데이터를 ppm 단위로 변환하고, 임계값 초과 여부를 분석합니다.
3. **경고 알림**: CO₂ 농도가 설정된 임계값을 초과하면 "이산화탄소 농도가 높습니다. 즉시 환기가 필요합니다."라는 음성 메시지가 출력됩니다.

## 📖 코드 설명

- **주요 모듈**
  - `tos`: TinyOS와의 통신을 위한 모듈로, Zigbee 프로토콜을 사용하여 Raspberry Pi와 센서 간의 데이터를 교환합니다.
  - `pyttsx3`: Python에서 음성 합성을 가능하게 하는 라이브러리로, CO₂ 농도가 임계값을 초과할 때 경고 메시지를 음성으로 출력하는 데 사용됩니다.
  ```python
  import tos
  import pyttsx3
  from datetime import datetime

- **CO₂ 임계값 설정**
  -`CO2_THRESHOLD`: 이 변수는 CO₂ 농도에 대한 임계값을 ppm 단위로 설정합니다. 기본값은 1000 ppm입니다. 환경에 따라 이 값을 조정하여 더 민감하거나 덜 민감한 경고를 설정할 수 있습니다.
  ```python
  CO2_THRESHOLD = 1000
  
- **음성 엔진 설정**
  - `engine`: `pyttsx3` 라이브러리를 사용하여 초기화된 음성 엔진입니다. 음성 메시지의 속도와 언어를 설정할 수 있습니다.
    - `setProperty('rate', 200)`: 음성 메시지의 속도를 설정합니다.
    - `setProperty('voice', 'Korean')`: 출력될 음성 메시지의 언어를 한국어로 설정합니다.
    ```python
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)  # 말하는 속도
    engine.setProperty('voice', 'korean')  # 음성 언어 설정
    
- **데이터 패킷 처리**
  - `OscilloscopeMsg`: 이 클래스는 수신된 데이터 패킷의 구조를 정의합니다. 각 필드는 센서 데이터의 다양한 측정값을 나타냅니다.
    - 패킷 데이터를 분석하여 CO₂ 농도 데이터를 추출하고, 필요에 따라 경고를 발생시키는 로직을 포함합니다.
  ```python
  class OscilloscopeMsg(tos.Packet):
    def __init__(self, packet=None):
        # 각 필드는 센서 데이터의 다양한 측정값을 나타냅니다
        tos.Packet.__init__(self,
                            [('srcID', 'int', 2),
                             ('seqNo', 'int', 4),
                             ('type', 'int', 2),
                             ('Data0', 'int', 2)],  # 주요 CO₂ 데이터 필드
                            packet)

- **데이터 수신 및 경고**
  - `am.read()`: 이 함수를 통해 데이터 수신이 이루어집니다. 수신된 데이터는 `OscilloscopeMsg` 형태로 변환되어 CO₂ 농도를 분석합니다.
  - `engine.say()`: CO₂ 농도가 설정된 임계값을 초과하면, 이 함수를 사용하여 경고 메시지를 음성으로 출력합니다.
  - `engine.runAndWait()`: 음성 출력을 실행합니다.
  ```python
  def read_sensor_data():
    am = tos.AM()
    while True:
        p = am.read()
        if p:
            msg = OscilloscopeMsg(p.data)
            co2_level = msg.Data0
            print(f"{datetime.now()} - CO₂ Level: {co2_level} ppm")
            if co2_level > CO2_THRESHOLD:
                warn_high_co2(co2_level)

## 🚀 실행 방법

1. **Raspberry Pi 설정**
   - 필요한 라이브러리를 설치합니다:
     ```bash
     pip install pyttsx3
     ```

2. **장비 연결**
   - CO₂ 센서를 Zigbee 모듈과 연결합니다.
   - Zigbee 모듈을 Raspberry Pi의 USB 포트에 연결합니다.

3. **코드 실행**
   - 아래 명령어를 실행합니다:
     ```bash
     python co2_detect.py serial@/dev/ttyUSB0:115200
     ```

4. **시스템 작동 확인**
   - CO₂ 농도가 실시간으로 출력됩니다.
   - 임계값 초과 시 음성 경고 메시지가 출력됩니다.
