// [중요] 가지고 계신 헬멧 영상을 프로젝트 폴더에 'helmet_intro.mp4'로 저장해주세요.
// 만약 파일명이 다르다면 아래 경로를 수정해야 합니다.
export const INTRO_VIDEO_URL = "/helmet_intro.mp4";

// 테스트용 (파일이 없을 경우를 대비한 예비 링크 주석 처리)
// export const INTRO_VIDEO_URL = "https://videos.pexels.com/video-files/852423/852423-hd_1920_1080_25fps.mp4";

export const CALIBRATION_DURATION_MS = 4000; // 분석 연출 시간
export const SUCCESS_MESSAGE_DURATION_MS = 2000; // 완료 메시지 표시 시간

// WebSocket connection URL
export const WEBSOCKET_URL = "ws://localhost:8000/ws";