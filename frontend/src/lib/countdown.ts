/**
 * Pure countdown / Azan logic (no React, fully testable).
 *
 * Spec (from CLAUDE.md):
 *  1. Next upcoming prayer comes from today's times; after Jacia (isha), target tomorrow's
 *     Sabahu (imsak).
 *  2. Live HH:MM:SS countdown to that prayer.
 *  3. Anchored to Europe/Belgrade (handled when building target instants).
 *  4. At 00:00:00, show "Koha e Ezanit" for the prayer that just entered, hold 60s.
 *  5. After 60s, switch the target to the next prayer.
 *
 * Sunrise (Lindja e Diellit) is display-only and is NOT part of the prayer/Azan sequence.
 */

import { belgradeWallClockToEpoch } from "./belgrade";

export const PRAYER_SEQUENCE = ["imsak", "dhuhr", "asr", "maghrib", "isha"] as const;
export type PrayerKey = (typeof PRAYER_SEQUENCE)[number];

export const AZAN_HOLD_MS = 60_000;

export interface CountdownTarget {
  key: PrayerKey;
  instant: number; // epoch ms
}

export type CountdownState =
  | { phase: "countdown"; key: PrayerKey; msRemaining: number }
  | { phase: "azan"; key: PrayerKey; msRemaining: number };

/**
 * Build the ordered list of prayer targets: today's five prayers plus tomorrow's Sabahu,
 * each as an absolute instant interpreted in Europe/Belgrade.
 */
export function buildTargets(
  todayIso: string,
  todayTimes: Record<PrayerKey, string>,
  tomorrowIso: string,
  tomorrowImsak: string,
): CountdownTarget[] {
  const targets: CountdownTarget[] = PRAYER_SEQUENCE.map((key) => ({
    key,
    instant: belgradeWallClockToEpoch(todayIso, todayTimes[key]),
  }));
  targets.push({ key: "imsak", instant: belgradeWallClockToEpoch(tomorrowIso, tomorrowImsak) });
  return targets;
}

/**
 * Determine the current countdown/azan state for `nowMs` against the ordered `targets`.
 * Returns null only if no targets were supplied.
 */
export function computeCountdown(
  nowMs: number,
  targets: CountdownTarget[],
  azanHoldMs: number = AZAN_HOLD_MS,
): CountdownState | null {
  if (targets.length === 0) return null;

  // A prayer that just entered holds the "Koha e Ezanit" announcement for azanHoldMs.
  for (const t of targets) {
    if (nowMs >= t.instant && nowMs < t.instant + azanHoldMs) {
      return { phase: "azan", key: t.key, msRemaining: t.instant + azanHoldMs - nowMs };
    }
  }

  const next = targets.find((t) => t.instant > nowMs);
  if (!next) return null;
  return { phase: "countdown", key: next.key, msRemaining: next.instant - nowMs };
}

/** Format milliseconds as HH:MM:SS (clamped at zero). */
export function formatHMS(ms: number): string {
  const total = Math.max(0, Math.floor(ms / 1000));
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(Math.floor(total / 3600))}:${pad(Math.floor((total % 3600) / 60))}:${pad(
    total % 60,
  )}`;
}
