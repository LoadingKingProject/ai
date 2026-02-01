export enum AppStage {
  BOOT_SEQUENCE = 'BOOT_SEQUENCE',   // Playing the intro video
  
  // New Face Analysis Stages
  FACE_SCANNING = 'FACE_SCANNING',   // Show Sniper Gauge, guide user position
  FACE_ANALYZING = 'FACE_ANALYZING', // Countdown & Analysis in progress
  FACE_REPORT = 'FACE_REPORT',       // Show Result & Wait for Approval
  
  // Hand Tracking Stage
  ACTIVE_MODE = 'ACTIVE_MODE',       // Full gesture control active
  
  // Deprecated (keep for backward compatibility if needed)
  CALIBRATING = 'CALIBRATING',
  CALIBRATION_COMPLETE = 'CALIBRATION_COMPLETE'
}

export interface SystemStatus {
  id: string;
  label: string;
  status: 'OK' | 'PENDING' | 'OFFLINE';
}
