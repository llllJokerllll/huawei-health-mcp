/**
 * Huawei Health MCP Server — Type Definitions
 */

/** Date range for queries */
export interface DateRange {
  start: string; // ISO 8601 date
  end: string;   // ISO 8601 date
}

/** Heart rate data point */
export interface HeartRateData {
  timestamp: string;
  value: number; // BPM
  type: 'instantaneous' | 'continuous' | 'resting' | 'exercise';
}

/** Sleep phase */
export type SleepPhase = 'deep' | 'light' | 'REM' | 'awake';

/** Sleep segment */
export interface SleepSegment {
  phase: SleepPhase;
  start: string;
  end: string;
  duration_minutes: number;
}

/** Sleep data */
export interface SleepData {
  date: string;
  bedtime: string;
  wakeup: string;
  duration_minutes: number;
  score: number; // 0-100
  phases: SleepSegment[];
  apnea_events: number;
  spo2_avg: number;
}

/** SpO2 data point */
export interface SpO2Data {
  timestamp: string;
  value: number; // Percentage 0-100
}

/** Steps data */
export interface StepsData {
  date: string;
  steps: number;
  distance_meters: number;
  calories: number;
}

/** Stress data point */
export interface StressData {
  timestamp: string;
  level: number; // 1-100
  description: 'relaxed' | 'normal' | 'moderate' | 'high' | 'very_high';
}

/** Temperature data point */
export interface TemperatureData {
  timestamp: string;
  value_celsius: number;
}

/** ECG data */
export interface ECGData {
  timestamp: string;
  result: 'normal' | 'sinus_rhythm_with_premature_beats' | 'atrial_fibrillation' | 'unknown';
  heart_rate: number;
}

/** Workout summary */
export interface WorkoutData {
  id: string;
  type: string;
  start: string;
  end: string;
  duration_minutes: number;
  calories: number;
  heart_rate_avg: number;
  heart_rate_max: number;
  distance_meters?: number;
}

/** Daily health summary */
export interface DailyHealthSummary {
  date: string;
  heart_rate_resting: number;
  heart_rate_avg: number;
  heart_rate_max: number;
  steps: number;
  calories_active: number;
  calories_total: number;
  sleep_hours: number;
  sleep_score: number;
  spo2_avg: number;
  stress_avg: number;
  temperature_avg: number;
  workouts: number;
}
