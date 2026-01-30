export enum AppStage {
  BOOT_SEQUENCE = 'BOOT_SEQUENCE',   // Playing the intro video
  CALIBRATING = 'CALIBRATING',       // Webcam active, analyzing user
  CALIBRATION_COMPLETE = 'CALIBRATION_COMPLETE', // Success state before transition
  ACTIVE_MODE = 'ACTIVE_MODE'        // Full gesture control active
}

export interface SystemStatus {
  id: string;
  label: string;
  status: 'OK' | 'PENDING' | 'OFFLINE';
}