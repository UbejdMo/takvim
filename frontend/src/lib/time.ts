/** Small display-formatting helpers for "HH:MM:SS" wall-clock strings and ISO dates. */

/** "HH:MM:SS" -> "HH:MM". */
export function hhmm(time: string): string {
  return time.slice(0, 5);
}

/** Gjatësia e ditës: maghrib − sunrise as "HH:MM" (display only). */
export function dayLength(sunrise: string, maghrib: string): string {
  const toMin = (t: string): number => {
    const [h = 0, m = 0] = t.split(":").map(Number);
    return h * 60 + m;
  };
  const diff = toMin(maghrib) - toMin(sunrise);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(Math.floor(diff / 60))}:${pad(diff % 60)}`;
}

/** Parse "YYYY-MM-DD" into a local Date (midnight), for display formatting only. */
export function parseIsoDate(iso: string): Date {
  const [y = 0, m = 1, d = 1] = iso.split("-").map(Number);
  return new Date(y, m - 1, d);
}

/** "YYYY-MM-DD" -> "DD.MM" for compact calendar/event display. */
export function dayMonth(iso: string): string {
  const [, m, d] = iso.split("-");
  return `${d}.${m}`;
}
