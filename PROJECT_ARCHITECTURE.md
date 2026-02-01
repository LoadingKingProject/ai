# PROJECT ARCHITECTURE - Air Mouse

**Generated:** 2026-02-01
**Version:** 1.2.0 (Face Analysis & Streaming Update)

---

## 1. 🏗️ SYSTEM ARCHITECTURE OVERVIEW

이 프로젝트는 **Python 백엔드(AI 연산)**와 **React 프론트엔드(UI/UX)**가 **WebSocket**을 통해 실시간으로 데이터를 주고받는 구조입니다.

```mermaid
graph TD
    User[User] -->|Webcam Feed| Backend(Python FastAPI)
    Backend -->|Base64 Image Stream| Frontend(React Client)
    Backend -->|Analysis Data (JSON)| Frontend
    Frontend -->|Control Signals| Backend
    Backend -->|Mouse/Keyboard Control| OS[Operating System]
```

### Key Components
| Component | Technology | Role |
|-----------|------------|------|
| **Backend** | Python, FastAPI, MediaPipe, OpenCV | AI 모델 추론, 영상 처리, 마우스 제어, WebSocket 서버 |
| **Frontend** | React, Vite, TypeScript, Tailwind | UI 렌더링, 사용자 인터랙션, 시각 효과(VisionOS Style) |
| **Protocol** | WebSocket (ws://) | 실시간 양방향 통신 (30fps) |

---

## 2. 🧠 AI MODELS & LOGIC

Google의 **MediaPipe** 솔루션을 사용하여 온디바이스 실시간 추론을 수행합니다. 성능 최적화를 위해 **순차적 모델 로딩(Sequential Loading)** 방식을 사용합니다.

### A. Face Analysis (초기 단계)
- **Model**: `MediaPipe Face Mesh` (468 Landmarks)
- **Role**: 사용자 거리 측정 및 얼굴 비율 분석.
- **Logic**:
  - **Distance Check**: 눈 너비 픽셀 비율을 계산하여 타겟 거리(1m) 유도.
  - **Ratio Analysis**: 눈, 코, 입, 얼굴형의 비율을 수치화하여 점수(Score) 및 랭크(S~C) 산출.
  - **Memory**: 사용 완료 후 메모리에서 **언로드(Unload)**됨.

### B. Hand Tracking (후기 단계)
- **Model**: `MediaPipe Hands` (21 Landmarks)
- **Role**: 손 제스처 인식 및 마우스 포인터 제어.
- **Logic**:
  - **Click**: 엄지-검지 거리 계산 (동적 임계값 적용).
  - **Zoom**: 엄지-중지 거리 계산.
  - **Swipe**: 손바닥 펼침 상태(`Palm Open`)에서 이동 속도 감지.
  - **Double Click**: 엄지-새끼손가락 접촉.

---

## 3. 🐍 BACKEND (FastAPI) implementation

FastAPI는 시스템의 **중추 신경** 역할을 하며, 비동기 처리를 통해 고속 데이터 전송을 담당합니다.

### 주요 기능
1.  **WebSocket Streaming**:
    - Windows의 웹캠 독점 문제를 해결하기 위해, 백엔드가 웹캠을 점유하고 프레임을 읽습니다.
    - 읽은 프레임을 `JPEG` 압축 -> `Base64` 인코딩하여 프론트엔드로 전송합니다.
    - AI 분석 데이터(`face_data`, `hand_data`)를 JSON으로 동기화하여 전송합니다.

2.  **State Machine (상태 관리)**:
    - `GlobalState`를 통해 앱의 흐름을 제어합니다.
    - `WAITING_FACE` → `ANALYZING` → `REPORT` → `ACTIVE`

3.  **Model Manager**:
    - 메모리 효율을 위해 상태에 따라 필요한 모델만 로드하고, 불필요한 모델은 `gc.collect()`로 해제합니다.

### API Endpoints
- `GET /health`: 서버 상태 확인.
- `POST /approve`: 얼굴 분석 결과 승인/거절 처리 (상태 전환 트리거).
- `WS /ws`: 실시간 데이터 및 영상 스트림 채널.

---

## 4. ⚛️ FRONTEND (React) implementation

React는 백엔드의 연산 결과를 시각적으로 표현하는 **뷰어(Viewer)** 역할에 집중합니다.

### 주요 컴포넌트
1.  **`WebcamFeed`**: 백엔드에서 받은 Base64 이미지를 `<img>` 태그로 렌더링합니다. (브라우저 웹캠 API 미사용)
2.  **`FaceSniperOverlay`**: Canvas API를 사용하여 부드러운 스나이퍼 게이지와 타겟팅 UI를 그립니다.
3.  **`FaceReportOverlay`**: 분석 결과에 따라 "ACCESS GRANTED"(성공) 또는 "ACCESS DENIED"(실패) 애니메이션을 보여줍니다.
4.  **`HandLandmarks`**: 손 랜드마크(21개 점)를 화면 위에 오버레이합니다.
5.  **`useWebSocket` (Custom Hook)**: WebSocket 연결 관리, 데이터 파싱, 이미지 디코딩, 상태 동기화를 담당합니다.

---

## 5. 🔄 DATA FLOW SCENARIO

1.  **Initial Connection**:
    - 클라이언트 접속 → WebSocket 연결 수립.
    - 백엔드 상태: `WAITING_FACE`.
    - Face Mesh 모델 로드.

2.  **Face Scanning Phase**:
    - 백엔드: 웹캠 프레임 캡처 -> Face Mesh 추론 -> 거리 계산 -> 이미지+데이터 전송.
    - 프론트엔드: 이미지 표시 + `FaceSniperOverlay`에 거리 정보 반영.

3.  **Analysis & Report**:
    - 거리 적중(Target Locked) -> 백엔드 상태 `ANALYZING` -> `REPORT`.
    - 결과 데이터(Score, Rank) 전송.
    - 프론트엔드: `FaceReportOverlay` 표시. 성공 시 `success.mp3` 재생 및 자동 승인 요청.

4.  **Active Mode (Hand Tracking)**:
    - 승인 신호 수신 -> 백엔드 상태 `ACTIVE`.
    - **Face Mesh 언로드** -> **Hands 모델 로드**.
    - 손 인식 데이터 전송 시작.
    - 프론트엔드: `HandLandmarks` 표시, 마우스 제어 시작.

---

## 6. 🚀 PERFORMANCE OPTIMIZATIONS

- **Sequential Loading**: 무거운 AI 모델 2개를 동시에 띄우지 않고 교체하며 실행하여 메모리 절약.
- **Base64 Streaming**: 웹캠 충돌 방지 및 저지연 영상 전송 (JPEG 압축률 70%).
- **Canvas Rendering**: React DOM 조작을 최소화하고 Canvas로 고성능 UI 렌더링.
- **Dynamic Threshold**: 손 크기에 비례한 가변 임계값을 사용하여 거리 변화에 강인한 제스처 인식 구현.
