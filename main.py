import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

# ==========================================
# [사용자 설정 영역]
# ==========================================
CAM_ID = 0  # 웹캠 번호 (노트북 내장: 0, 외장: 1)
CAM_WIDTH = 640  # 카메라 가로 해상도
CAM_HEIGHT = 480  # 카메라 세로 해상도
SMOOTHING = 5  # 마우스 반응 속도 (클수록 부드럽지만 느림, 1~10 추천)
CLICK_DIST = 30  # 클릭 인식 거리 (엄지-검지 사이 거리)
FRAME_R = 100  # 인식 영역 제한 (화면 가장자리 여백)
# ==========================================


def calculate_screen_position(x, y, frame_r, cam_w, cam_h, screen_w, screen_h):
    """Convert webcam coordinates to screen coordinates.

    Transforms hand position coordinates from webcam frame (with edge margins)
    to monitor screen coordinates using linear interpolation.

    Args:
        x: X coordinate from webcam (0 to cam_w)
        y: Y coordinate from webcam (0 to cam_h)
        frame_r: Recognition area margin (pixels from edge)
        cam_w: Camera frame width (pixels)
        cam_h: Camera frame height (pixels)
        screen_w: Monitor screen width (pixels)
        screen_h: Monitor screen height (pixels)

    Returns:
        Tuple of (screen_x, screen_y) - coordinates mapped to screen resolution
    """
    screen_x = np.interp(x, (frame_r, cam_w - frame_r), (0, screen_w))
    screen_y = np.interp(y, (frame_r, cam_h - frame_r), (0, screen_h))
    return screen_x, screen_y


def run_smart_presenter():
    # 1. 카메라 및 AI 모델 초기화
    cap = cv2.VideoCapture(CAM_ID)
    cap.set(3, CAM_WIDTH)
    cap.set(4, CAM_HEIGHT)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,  # 한 손만 인식
        min_detection_confidence=0.7,  # 탐지 신뢰도
        min_tracking_confidence=0.7,  # 추적 신뢰도
    )
    mp_draw = mp.solutions.drawing_utils

    # 모니터 해상도 가져오기
    screen_w, screen_h = pyautogui.size()

    # 스무딩을 위한 이전 좌표/현재 좌표 변수
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0

    # PyAutoGUI 안전장치 해제 (화면 구석으로 가면 멈추는 기능 끄기)
    pyautogui.FAILSAFE = False

    print("✅ 시스템 시작! 'q'를 누르면 종료됩니다.")

    while True:
        success, img = cap.read()
        if not success:
            print("웹캠을 찾을 수 없습니다.")
            break

        # 2. 이미지 전처리
        # 거울 모드 (좌우 반전) - 중요!
        img = cv2.flip(img, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 3. 손 추적 수행
        results = hands.process(img_rgb)

        # 인식 영역 박스 그리기 (이 안에서만 손을 움직이세요)
        cv2.rectangle(
            img,
            (FRAME_R, FRAME_R),
            (CAM_WIDTH - FRAME_R, CAM_HEIGHT - FRAME_R),
            (255, 0, 255),
            2,
        )

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                lmList = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                if len(lmList) != 0:
                    # 좌표 추출: 8번(검지 끝), 4번(엄지 끝)
                    x1, y1 = lmList[8][1], lmList[8][2]
                    x2, y2 = lmList[4][1], lmList[4][2]

                    # 4. 마우스 이동 (검지)
                    # 좌표 변환: 웹캠 좌표(640x480) -> 모니터 좌표(1920x1080)
                    x3, y3 = calculate_screen_position(
                        x1, y1, FRAME_R, CAM_WIDTH, CAM_HEIGHT, screen_w, screen_h
                    )

                    # 스무딩 적용 (떨림 방지)
                    clocX = plocX + (x3 - plocX) / SMOOTHING
                    clocY = plocY + (y3 - plocY) / SMOOTHING

                    # 마우스 커서 이동
                    try:
                        pyautogui.moveTo(clocX, clocY)
                    except:
                        pass  # 화면 밖으로 나가는 에러 방지

                    plocX, plocY = clocX, clocY

                    # 5. 클릭 감지 (엄지 + 검지)
                    distance = np.hypot(x2 - x1, y2 - y1)

                    # 클릭 상태 시각화
                    if distance < CLICK_DIST:
                        cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)  # 초록색
                        pyautogui.click()
                    else:
                        cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)  # 빨간색

        # 6. 화면 출력 및 종료
        cv2.putText(
            img,
            "Exit: Press 'q'",
            (10, 30),
            cv2.FONT_HERSHEY_PLAIN,
            1.5,
            (0, 255, 0),
            2,
        )
        cv2.imshow("Smart Presenter AI", img)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_smart_presenter()
