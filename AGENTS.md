# PROJECT KNOWLEDGE BASE - Air Mouse

**Generated:** 2026-01-30
**Status:** New Project (초기 설정 필요)

---

## 📋 OVERVIEW

Air Mouse 프로젝트입니다. 현재 초기 단계로, 코드베이스가 구성되기 전입니다.
이 문서는 프로젝트가 발전함에 따라 업데이트해야 합니다.

---

## 🚀 QUICK START

```bash
# 프로젝트 초기화 (예시 - 프레임워크에 따라 수정 필요)
npm init -y          # Node.js
cargo init           # Rust
python -m venv venv  # Python

# 의존성 설치
npm install          # Node.js
cargo build          # Rust
pip install -r requirements.txt  # Python
```

---

## 🔧 BUILD / TEST / LINT COMMANDS

### Testing

#### 테스트 의존성 설치
```bash
pip install -r requirements-dev.txt
```

#### 전체 테스트 실행
```bash
pytest -v
```

#### 단일 테스트 파일 실행
```bash
pytest tests/test_coordinate.py -v
pytest tests/test_smoothing.py -v
pytest tests/test_click.py -v
pytest tests/test_landmarks.py -v
```

#### 커버리지 리포트 포함
```bash
pytest --cov=. --cov-report=term-missing
```

#### 특정 마커로 테스트 실행
```bash
pytest -m unit          # 모든 unit 테스트 실행
pytest -m integration   # 모든 integration 테스트 실행
```

#### 테스트 파일 설명
- `tests/test_coordinate.py`: `calculate_screen_position()` 함수 테스트 (4개 테스트)
- `tests/test_smoothing.py`: `apply_smoothing()` 함수 테스트 (4개 테스트)
- `tests/test_click.py`: `detect_click()` 함수 테스트 (5개 테스트)
- `tests/test_landmarks.py`: `extract_landmarks()` 함수 테스트 (3개 테스트)

### Build
```bash
# Python 프로젝트 (빌드 필요 없음)
# 실행: python main.py
```

### Lint
```bash
ruff check .         # Python Ruff
```

### Format
```bash
ruff format .        # Python
```

---

## 📁 PROJECT STRUCTURE

> **프로젝트 구조 확정 후 업데이트**

```
Air Mouse/
├── AGENTS.md         # 이 파일
├── src/              # 소스 코드 (예정)
│   ├── main.*        # 엔트리 포인트
│   └── ...
├── tests/            # 테스트 코드 (예정)
├── docs/             # 문서 (예정)
└── README.md         # 프로젝트 소개 (예정)
```

---

## 🎨 CODE STYLE GUIDELINES

### 일반 원칙
- **명확성 우선**: 짧은 코드보다 읽기 쉬운 코드
- **일관성 유지**: 기존 패턴을 따름
- **문서화**: 복잡한 로직에는 주석 추가

### Naming Conventions

| 요소 | 스타일 | 예시 |
|------|--------|------|
| 변수/함수 | camelCase 또는 snake_case | `mousePosition`, `mouse_position` |
| 클래스/타입 | PascalCase | `AirMouseController` |
| 상수 | SCREAMING_SNAKE_CASE | `MAX_VELOCITY` |
| 파일명 | kebab-case 또는 snake_case | `air-mouse.ts`, `air_mouse.py` |

### Import 순서
```
1. 표준 라이브러리
2. 외부 패키지/서드파티
3. 내부 모듈 (절대 경로)
4. 내부 모듈 (상대 경로)
```

### Error Handling
```typescript
// ✅ 좋음: 명시적 에러 처리
try {
  await connectMouse();
} catch (error) {
  logger.error('마우스 연결 실패:', error);
  throw new ConnectionError('마우스 연결에 실패했습니다', { cause: error });
}

// ❌ 나쁨: 빈 catch 블록
try {
  await connectMouse();
} catch (e) {}
```

### Type Safety (TypeScript/Typed Languages)
```typescript
// ❌ 금지
const data = response as any;
// @ts-ignore
// @ts-expect-error

// ✅ 권장
interface MouseData {
  x: number;
  y: number;
  velocity: number;
}
const data: MouseData = validateResponse(response);
```

---

## 🚨 HARD RULES (반드시 준수)

1. **타입 안전성**: `as any`, `@ts-ignore` 사용 금지
2. **빈 catch 블록 금지**: 모든 에러는 명시적으로 처리
3. **커밋 전 검증**: lint/test 통과 필수
4. **시크릿 관리**: API 키, 비밀번호는 환경변수 사용

---

## 🧪 TESTING GUIDELINES

### 테스트 파일 위치
- 소스 파일과 같은 디렉토리: `*.test.ts`, `*.spec.ts`
- 또는 별도 tests/ 디렉토리

### 테스트 작성 패턴
```typescript
describe('AirMouse', () => {
  describe('connect()', () => {
    it('should establish connection with valid config', async () => {
      // Arrange
      const config = createTestConfig();
      
      // Act
      const result = await mouse.connect(config);
      
      // Assert
      expect(result.connected).toBe(true);
    });
  });
});
```

---

## 📝 GIT WORKFLOW

### Commit Message Format
```
<type>(<scope>): <subject>

<body>
```

### Types
- `feat`: 새 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 포맷팅 (코드 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

### 예시
```
feat(mouse): 제스처 인식 기능 추가

- 스와이프 제스처 감지 로직 구현
- 제스처별 콜백 핸들러 추가
```

---

## 🔍 WHERE TO LOOK

| 작업 | 위치 | 참고 |
|------|------|------|
| 엔트리 포인트 | `src/main.*` | 앱 시작점 |
| 비즈니스 로직 | `src/` | 핵심 기능 |
| 테스트 | `tests/` 또는 `*.test.*` | 테스트 코드 |
| 설정 | `*.config.*`, `.*rc` | 빌드/린트 설정 |

---

## 📚 REFERENCE

- [Project README](./README.md) - 프로젝트 개요 (작성 예정)
- [API Documentation](./docs/api.md) - API 문서 (작성 예정)

---

## ⚠️ TODO: 프로젝트 설정 후 업데이트 필요

- [ ] 실제 사용 언어/프레임워크에 맞게 명령어 수정
- [ ] 디렉토리 구조 업데이트
- [ ] 린트/포맷 설정 파일 경로 추가
- [ ] CI/CD 워크플로우 문서화
