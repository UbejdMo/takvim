/**
 * Europe/Belgrade time helpers.
 *
 * All "today / now" logic in the app is anchored to Europe/Belgrade, NOT the user's device
 * timezone (Immutable rule #5), so the countdown stays correct for users abroad.
 *
 * The technique: epoch milliseconds are an absolute, timezone-independent instant. We convert
 * BIK's wall-clock prayer times (interpreted in Europe/Belgrade) into absolute instants, and
 * the countdown then just subtracts `Date.now()` — correct on any device.
 */

const TZ = "Europe/Belgrade";

const partsFormatter = new Intl.DateTimeFormat("en-US", {
  timeZone: TZ,
  hourCycle: "h23",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
});

function fields(epochMs: number): Record<string, number> {
  const out: Record<string, number> = {};
  for (const part of partsFormatter.formatToParts(new Date(epochMs))) {
    if (part.type !== "literal") out[part.type] = Number(part.value);
  }
  return out;
}

/** Offset (ms) of Europe/Belgrade ahead of UTC at the given instant (handles DST). */
export function belgradeOffsetMs(epochMs: number): number {
  const f = fields(epochMs);
  const asUtc = Date.UTC(f.year, f.month - 1, f.day, f.hour, f.minute, f.second);
  return asUtc - epochMs;
}

/** Today's date in Europe/Belgrade as "YYYY-MM-DD". */
export function belgradeToday(epochMs: number = Date.now()): string {
  const f = fields(epochMs);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${f.year}-${pad(f.month)}-${pad(f.day)}`;
}

/** The Belgrade calendar day after `isoDate` ("YYYY-MM-DD"), as "YYYY-MM-DD". */
export function nextDay(isoDate: string): string {
  const [y, m, d] = isoDate.split("-").map(Number);
  const next = new Date(Date.UTC(y, m - 1, d + 1));
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${next.getUTCFullYear()}-${pad(next.getUTCMonth() + 1)}-${pad(next.getUTCDate())}`;
}

/**
 * Convert a Europe/Belgrade wall-clock date+time into absolute epoch milliseconds.
 * `isoDate` is "YYYY-MM-DD"; `time` is "HH:MM" or "HH:MM:SS".
 */
export function belgradeWallClockToEpoch(isoDate: string, time: string): number {
  const [y, mo, d] = isoDate.split("-").map(Number);
  const [h, mi, s = 0] = time.split(":").map(Number);
  const naiveUtc = Date.UTC(y, mo - 1, d, h, mi, s);
  // Subtract the offset to land on the real instant; refine once for DST transition days.
  let epoch = naiveUtc - belgradeOffsetMs(naiveUtc);
  const refinedOffset = belgradeOffsetMs(epoch);
  epoch = naiveUtc - refinedOffset;
  return epoch;
}
