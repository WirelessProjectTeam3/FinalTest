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

### TinyOS와의 통신 (tos 모듈)
-  TinyOS는 센서 네트워크를 위한 운영 체제로, 본 프로젝트에서는 Raspberry Pi와 CO₂ 센서 간의 데이터 통신을 관리합니다.
-  `tos` 모듈을 통해 Zigbee 프로토콜을 사용하여 Raspberry Pi와 센서 간에 데이터를 안전하고 신뢰성 있게 전송합니다. 이 모듈은 센서에서 수집된 데이터 패킷을 Raspberry Pi로 전송하는 데 필수적입니다.

    ```python
    import tos
    am = tos.AM()


### 데이터 패킷 처리 (OscilloscopeMsg 클래스) 
- 수신된 데이터를 구조화하고, 각 센서 데이터 포인트를 적절히 파싱하여 CO₂ 농도를 계산합니다.
- OscilloscopeMsg 클래스는 TinyOS 패킷 구조를 정의하며, 센서 데이터를 다루는 필드를 포함합니다. 이 클래스를 통해 센서 데이터의 CO₂ 농도를 추출하고, 필요한 경우 경고 로직을 실행합니다.

    ```python
    class OscilloscopeMsg(tos.Packet):
        def __init__(self, packet=None):
            tos.Packet.__init__(self,
                                [('srcID', 'int', 2),
                                 ('seqNo', 'int', 4),
                                 ('type', 'int', 2),
                                 ('Data0', 'int', 2)],  # CO₂ 데이터 필드
                                packet)

### CO₂ 농도 계산
- 센서로부터의 CO₂ 측정값은 아날로그 신호로 출력되며, 이를 디지털 값으로 변환하여 처리합니다. 이 변환 과정에서 사용된 계산식은 다음과 같습니다:
    ```python
    CO2 = 1.5 * CO2 / 4096 * 2 * 1000  # 데이터 변환 (ppm)

- 계산식의 세부 요소:
    - 원시 데이터 (CO2): 센서에서 측정된 CO₂ 농도의 원시 아날로그 신호를 ADC를 통해 변환한 디지털 값입니다.
    - 분모의 4096: 12비트 ADC의 최대 분해능을 나타냅니다.
    - 계수 1.5와 2:
        - 1.5: 센서의 최대 감지 가능 CO₂ 농도를 조정합니다.
        - 2: 측정 범위를 확장하여 더 높은 농도를 측정할 수 있게 합니다.
    - 1000의 곱셈: 최종 값을 ppm 단위로 변환합니다.


### 음성 출력 (pyttsx3 모듈)
  - pyttsx3는 Python에서 작동하는 텍스트-투-스피치 변환 라이브러리로, CO₂ 농도가 임계값을 초과할 때 사용자에게 즉각적인 음성 경고를 제공합니다.
  - 이 모듈을 초기화하고, 음성 속도 및 언어 설정을 한국어로 조정하여 경고 메시지를 명확하게 전달합니다.
      ```python
         import pyttsx3
         engine = pyttsx3상](https://example.com/path/to/thumbnail.jpg)](https://photos.onedrive.com/share/0D986CDA029689A1!sabebe9e726e640689f1b8fedf1a4e9f8?cid=0D986CDA029689A1&resId=0D986CDA029689A1!sabebe9e726e640689f1b8fedf1a4e9f8&ithint=video&e=4%3aQNL5Go&sharingv2=true&fromShare=true&at=9&migratedtospo=true&redeem=aHR0cHM6Ly8xZHJ2Lm1zL3YvYy8wZDk4NmNkYTAyOTY4OWExL0VlZnA2NnZtSm1oQW54dVA3ZkdrNmZnQmV1Q0ZvWDJIRzc4TXUzdjVTbHYzTVE_ZT00OlFOTDVHbyZzaGFyaW5ndjI9dHJ1ZSZmcm9tU2hhcmU9dHJ1ZSZhdD05 "Video Title on OneDrive")


