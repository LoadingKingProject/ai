# 🖱️ Air Mouse: AI-Powered Touchless Interface

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=flat-square&logo=react&logoColor=black)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-00C0FF?style=flat-square)

<p align="center">
  <img src="https://github.com/user-attachments/assets/6e07af12-72ec-47b3-926d-d6012ab1df93" width="100%" alt="Air Mouse Main Concept" />
</p>

> **"비접촉 제스처로 제어하는 미래형 인터페이스"**
> 물리적 장치 없이 웹캠 하나로 마우스를 제어하고 시스템을 핸들링하는 Open-Source 프로젝트입니다.

---

## 1. 프로젝트 개요 (Problem & Solution)

### 1.1 문제 정의
현대의 컴퓨팅 환경은 물리적 입력 장치에 의존합니다. 하지만 **발표, 키오스크 사용, 요리 중 레시피 확인** 등 장치를 직접 만지기 어려운 상황이 빈번합니다. **Air Mouse**는 이러한 물리적 제약을 극복하기 위해 탄생했습니다.

### 1.2 핵심 AI 기술 및 선택 사유
* **Face Analysis**: `MediaPipe Face Mesh` (468 랜드마크)
* **Hand Tracking**: `MediaPipe Hands` (21 랜드마크)

#### 💡 선택 이유
1.  **실시간 온디바이스 처리**: 고사양 GPU 없이 CPU만으로 **30fps 이상의 추론**이 가능합니다.
2.  **프라이버시 및 저지연**: 영상 데이터를 서버로 보내지 않아 보안성이 뛰어나고 네트워크 지연을 최소화합니다.
3.  **플랫폼 호환성**: Python(Back)과 JS(Front) 환경 모두를 지원하여 확장에 용이합니다.

---

## 2. 시스템 아키텍처 및 데이터 파이프라인

<p align="center">
  <img src="https://github.com/user-attachments/assets/f17a0822-965d-4eff-a889-c02ee1c9ca03" width="48%" />
  <img src="https://github.com/user-attachments/assets/3c43881a-8fa8-4c0f-8ef7-4a08b6bc6f58" width="48%" />
</p>

### 2.1 데이터 흐름 (INPUT/OUTPUT)

| 단계 | INPUT | PROCESS | OUTPUT |
| :---: | :--- | :--- | :---: |
| **1** | **Webcam Feed** | **전처리**: 좌우 반전, RGB 변환, Base64 인코딩 | Pre-processed Frame |
| **2** | **Processed Frame** | **AI 추론**: Face Mesh 및 Hand 관절 검출 | Landmarks (x, y, z) |
| **3** | **Landmarks** | **후처리**: 스무딩(Jitter 제거), 동적 임계값 적용 | **Action Signal** |

### 2.2 핵심 전처리 기술
* **좌표 정규화**: 화면 해상도 독립적인 0.0~1.0 좌표계 사용.
* **이동 평균 필터 (Moving Average)**: 손 떨림 방지를 통해 부드러운 커서 이동 구현.
* **동적 임계값 (Dynamic Threshold)**: 카메라와의 거리에 비례하여 클릭/줌 인식 거리 자동 조절.

---

## 3. 성능 지표 및 한계점

### 3.1 성능 평가
* **인식 오차**: 정면 기준 거리 측정 오차 **±5cm 이내**.
* **처리 속도**: i5 CPU 기준 평균 **28~32 FPS** 유지.
* **응답 속도 (Latency)**: 입력부터 동작까지 **50~80ms** (체감 지연 거의 없음).

### 3.2 한계점 및 개선 방향
* **한계**: 역광 등 조명 환경 변화 및 손이 가려지는(Occlusion) 상황에서의 인식 저하.
* **개선**: 단순 거리 기반 로직 대신 **제스처 분류용 별도 모델(MobileNet 등)**을 파인튜닝하여 결합 예정.

---

## 4. 활용 가치 (UX)

### 4.1 적용 시나리오
* **데스크탑**: PPT 프레젠테이션 포인터 및 접근성 보조 도구.
* **공공 장소**: 비접촉 주문 시스템(키오스크), 위생이 중요한 병원 인터페이스.
* **홈 서비스**: 스마트 미러, 요리 앱 스크롤링 등.

### 4.2 사용자 경험
* **Pain Point 해결**: "연단으로 돌아가 마우스를 잡아야 하는 번거로움" 또는 "액정 오염" 걱정 해소.
* **Immersive UI**: VisionOS 스타일의 UI와 사운드 피드백을 통해 몰입감 있는 조작 환경 제공.

---

## 🛠️ 시작하기 (Quick Start)

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
