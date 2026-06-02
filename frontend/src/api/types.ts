/**
 * App-facing API types. These mirror the FastAPI Pydantic schemas.
 *
 * `npm run gen:api` writes the OpenAPI-derived types to `generated.ts` (gitignored); use it to
 * verify these stay in sync with the backend contract (CLAUDE.md convention).
 */

export type Region = "kosova" | "lugina";
export type EventType = "day" | "night" | "holiday";

export interface City {
  slug: string;
  name_sq: string;
  name_en: string;
  latitude: number;
  longitude: number;
  region: Region;
}

/** Times are local Kosovo wall-clock, serialized as "HH:MM:SS". */
export interface PrayerTimes {
  date: string; // "YYYY-MM-DD"
  imsak: string;
  sunrise: string;
  dhuhr: string;
  asr: string;
  maghrib: string;
  isha: string;
}

export interface IslamicEvent {
  date: string;
  hijri_label: string;
  name_sq: string;
  name_en: string;
  type: EventType;
  description_sq: string | null;
  description_en: string | null;
}

export interface Qibla {
  city: string;
  latitude: number;
  longitude: number;
  bearing: number;
  distance_km: number;
}
