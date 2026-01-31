# PROJECT KNOWLEDGE BASE - Air Mouse

**Generated:** 2026-01-30
**Status:** Active Development

---

## 📋 OVERVIEW

Air Mouse는 웹캠을 통해 손 제스처를 인식하여 마우스와 키보드를 제어하는 프로젝트입니다.

**구성:**
- **Backend (Python)**: FastAPI + WebSocket + MediaPipe + PyAutoGUI
- **Frontend (React)**: Vite + TypeScript + VisionOS 스타일 UI

---

## 🚀 QUICK START

### 의존성 설치

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 개발 서버 실행

**Windows (PowerShell):**
```powershell
.\scripts\dev.ps1
```

**Unix/macOS:**
```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

**개별 실행:**
```bash
# Backend (Terminal 1)
cd backend && python main.py
# → http://localhost:8000

# Frontend (Terminal 2)
cd frontend && npm run dev
# → http://localhost:3000
```

---

## 🔧 BUILD / TEST / LINT COMMANDS

### Backend (Python)

```bash
# 서버 실행
cd backend && python main.py

# Health check
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# 의존성 설치
pip install -r backend/requirements.txt
```

### Frontend (React)

```bash
# 개발 서버
cd frontend && npm run dev

# 빌드
cd frontend && npm run build

# TypeScript 검증
cd frontend && npx tsc --noEmit
```

### 테스트

```bash
# Python 테스트
pytest -v

# 개별 테스트
pytest tests/test_coordinate.py -v
pytest tests/test_smoothing.py -v
pytest tests/test_click.py -v
pytest tests/test_landmarks.py -v

# 커버리지
pytest --cov=. --cov-report=term-missing
```

### Lint

```bash
ruff check .         # Python
ruff format .        # Python 포맷팅
```

---

## 📁 PROJECT STRUCTURE

```
Air Mouse/
├── backend/                    # Python 백엔드
│   ├── main.py                 # FastAPI + WebSocket 서버
│   ├── hand_tracker.py         # MediaPipe 손 인식
│   ├── mouse_controller.py     # PyAutoGUI 마우스 제어
│   └── requirements.txt        # Python 의존성
│
├── frontend/                   # React 프론트엔드
│   ├── src/
│   │   ├── App.tsx             # 메인 앱 컴포넌트
│   │   ├── components/
│   │   │   ├── HandLandmarks.tsx   # 손 랜드마크 Canvas 오버레이
│   │   │   ├── HUDOverlay.tsx      # VisionOS 스타일 HUD
│   │   │   ├── WebcamFeed.tsx      # 웹캠 비디오 표시
│   │   │   └── VideoBackground.tsx # 인트로 비디오
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts     # WebSocket 연결 훅
│   │   ├── types/
│   │   │   ├── index.ts            # AppStage 등
│   │   │   └── websocket.ts        # WebSocket 메시지 타입
│   │   ├── constants/
│   │   │   └── index.ts            # 상수 (URL 등)
│   │   └── styles/
│   │       └── globals.css         # 글로벌 스타일
│   ├── package.json
│   └── vite.config.ts
│
├── scripts/
│   ├── dev.ps1                 # Windows 개발 스크립트
│   └── dev.sh                  # Unix 개발 스크립트
│
├── tests/                      # Python 테스트
├── main.py                     # (레거시 - 참조용)
└── AGENTS.md                   # 이 파일
```

---

## 🎮 GESTURE TYPES

| 제스처 | 동작 | 트리거 |
|--------|------|--------|
| `none` | 마우스 이동 | 검지만 펴기 |
| `click` / `drag` | 클릭/드래그 | 엄지 + 검지 붙이기 |
| `zoom` | 스크롤 줌 | 엄지 + 중지 붙이기 |
| `swipe_left` / `swipe_right` | 좌/우 화살표 | 손바닥 펴고 좌우 이동 |
| `palm_open` | 스와이프 대기 | 손바닥 펴기 |

---

## 🌐 API ENDPOINTS

### REST

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | 서버 상태 확인 |
| GET | `/status` | 카메라, FPS 정보 |

### WebSocket

| Endpoint | Direction | Description |
|----------|-----------|-------------|
| `/ws` | Server → Client | 손 인식 데이터 (30fps) |

**메시지 형식:**
```json
{
  "type": "hand_data",
  "landmarks": [{"id": 0, "x": 0.5, "y": 0.3}, ...],
  "gesture": "none",
  "mouse_position": {"x": 960, "y": 540},
  "is_palm_open": false,
  "fps": 30,
  "timestamp": 1706000000000
}
```

---

## 🎨 CODE STYLE GUIDELINES

### Python (Backend)
- **스타일**: snake_case
- **Linter**: Ruff
- **타입 힌트**: 필수

### TypeScript (Frontend)
- **스타일**: camelCase (변수/함수), PascalCase (컴포넌트/타입)
- **절대 금지**: `as any`, `@ts-ignore`
- **검증**: `npx tsc --noEmit`

---

## 🚨 HARD RULES

1. **타입 안전성**: `as any`, `@ts-ignore` 사용 금지
2. **빈 catch 블록 금지**: 모든 에러는 명시적으로 처리
3. **커밋 전 검증**: TypeScript 컴파일, lint 통과 필수
4. **시크릿 관리**: API 키는 환경변수 (.env.local) 사용

---

## 📝 GIT WORKFLOW

### Commit Message Format
```
<type>(<scope>): <subject>
```

### Types
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `refactor`: 리팩토링
- `test`: 테스트

### 예시
```
feat(backend): implement FastAPI WebSocket server
fix(frontend): resolve TypeScript compilation errors
```

---

## 🔍 WHERE TO LOOK

| 작업 | 위치 |
|------|------|
| WebSocket 서버 | `backend/main.py` |
| 손 인식 로직 | `backend/hand_tracker.py` |
| 마우스 제어 | `backend/mouse_controller.py` |
| React 앱 진입점 | `frontend/src/App.tsx` |
| WebSocket 훅 | `frontend/src/hooks/useWebSocket.ts` |
| 손 시각화 | `frontend/src/components/HandLandmarks.tsx` |
| HUD UI | `frontend/src/components/HUDOverlay.tsx` |
| 타입 정의 | `frontend/src/types/websocket.ts` |
