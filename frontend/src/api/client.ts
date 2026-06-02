import type { City, IslamicEvent, PrayerTimes, Qibla } from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

type Params = Record<string, string | number>;

async function get<T>(path: string, params?: Params): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`, window.location.origin);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      url.searchParams.set(key, String(value));
    }
  }
  const resp = await fetch(url.toString(), { headers: { Accept: "application/json" } });
  if (!resp.ok) {
    throw new Error(`API ${resp.status} on ${path}`);
  }
  return (await resp.json()) as T;
}

export const api = {
  cities: () => get<City[]>("/cities"),
  todayTimes: (city: string) => get<PrayerTimes>("/prayer-times/today", { city }),
  timesOnDate: (city: string, date: string) =>
    get<PrayerTimes>("/prayer-times", { city, date }),
  month: (city: string, year: number, month: number) =>
    get<PrayerTimes[]>("/prayer-times/month", { city, year, month }),
  year: (city: string, year: number) => get<PrayerTimes[]>("/prayer-times/year", { city, year }),
  events: (year: number) => get<IslamicEvent[]>("/events", { year }),
  eventToday: () => get<IslamicEvent | null>("/events/today"),
  qibla: (city: string) => get<Qibla>("/qibla", { city }),
};
