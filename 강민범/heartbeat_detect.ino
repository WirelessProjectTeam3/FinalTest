#include <PulseSensorPlayground.h>  // PulseSensorPlayground 라이브러리 포함
// #define USE_ARDUINO_INTERRUPTS true
// 변수 선언
const int PulseWire = 0;       // PulseSensor의 보라색 와이어를 아날로그 핀 0에 연결
const int LED = LED_BUILTIN;   // 아두이노 내장 LED 핀, 보통 핀 13에 가까이 있음
int Threshold = 500;          // 심박으로 인식할 신호의 임계값 설정

// PulseSensorPlayground 객체 생성
PulseSensorPlayground pulseSensor;

void setup() {
  Serial.begin(9600);  // 시리얼 모니터 시작

  // PulseSensor 객체 설정
  pulseSensor.analogInput(PulseWire);
  pulseSensor.blinkOnPulse(LED);       // 심박이 감지되면 자동으로 아두이노 LED를 깜빡이도록 설정
  pulseSensor.setThreshold(Threshold);

  // PulseSensor 객체가 제대로 생성되었는지 확인
  if (pulseSensor.begin()) {
    Serial.println("We created a pulseSensor Object !");  // 아두이노가 전원에 연결되거나 리셋될 때 한 번 출력
  }
}

void loop() {
  if (pulseSensor.sawStartOfBeat()) {            // 심박이 감지되었는지 지속적으로 확인
    int myBPM = pulseSensor.getBeatsPerMinute();  // BPM(분당 심박수) 값을 가져옴
    Serial.println(myBPM);  // BPM 값을 시리얼 플로터에 출력
  }

  delay(1000);  // 간단한 스케치에서 권장되는 지연 시간
}