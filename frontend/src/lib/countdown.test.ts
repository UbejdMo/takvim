import { describe, expect, it } from "vitest";

import { belgradeOffsetMs, belgradeWallClockToEpoch } from "./belgrade";
import {
  AZAN_HOLD_MS,
  type CountdownTarget,
  computeCountdown,
  formatHMS,
} from "./countdown";

const MIN = 60_000;
const HOUR = 60 * MIN;

// Synthetic targets on a simple numeric timeline (tz-independent).
const targets: CountdownTarget[] = [
  { key: "imsak", instant: 5 * HOUR },
  { key: "dhuhr", instant: 12 * HOUR },
  { key: "asr", instant: 16 * HOUR },
  { key: "maghrib", instant: 20 * HOUR },
  { key: "isha", instant: 22 * HOUR },
  { key: "imsak", instant: 29 * HOUR }, // tomorrow's Sabahu
];

describe("computeCountdown", () => {
  it("counts down to the first prayer before dawn", () => {
    const state = computeCountdown(3 * HOUR, targets);
    expect(state).toEqual({ phase: "countdown", key: "imsak", msRemaining: 2 * HOUR });
  });

  it("counts down to the next prayer mid-day", () => {
    const state = computeCountdown(13 * HOUR, targets);
    expect(state).toEqual({ phase: "countdown", key: "asr", msRemaining: 3 * HOUR });
  });

  it("enters Azan exactly when the prayer time hits (00:00:00)", () => {
    const state = computeCountdown(12 * HOUR, targets);
    expect(state?.phase).toBe("azan");
    expect(state?.key).toBe("dhuhr");
  });

  it("holds the Azan announcement for 60 seconds", () => {
    const within = computeCountdown(12 * HOUR + 59_000, targets);
    expect(within?.phase).toBe("azan");
    expect(within?.key).toBe("dhuhr");
  });

  it("switches to the next prayer after the 60s hold", () => {
    const after = computeCountdown(12 * HOUR + AZAN_HOLD_MS, targets);
    expect(after).toEqual({ phase: "countdown", key: "asr", msRemaining: 4 * HOUR - AZAN_HOLD_MS });
  });

  it("targets tomorrow's Sabahu after Jacia", () => {
    const state = computeCountdown(23 * HOUR, targets);
    expect(state).toEqual({ phase: "countdown", key: "imsak", msRemaining: 6 * HOUR });
  });

  it("returns null with no targets", () => {
    expect(computeCountdown(0, [])).toBeNull();
  });
});

describe("formatHMS", () => {
  it("formats hours, minutes, seconds", () => {
    expect(formatHMS(2 * HOUR + 3 * MIN + 4000)).toBe("02:03:04");
  });
  it("clamps negatives to zero", () => {
    expect(formatHMS(-5000)).toBe("00:00:00");
  });
});

describe("belgrade timezone conversion", () => {
  it("uses +1h (CET) in winter and +2h (CEST) in summer", () => {
    const winter = belgradeWallClockToEpoch("2026-01-15", "12:00");
    const summer = belgradeWallClockToEpoch("2026-07-15", "12:00");
    expect(belgradeOffsetMs(winter)).toBe(1 * HOUR);
    expect(belgradeOffsetMs(summer)).toBe(2 * HOUR);
  });

  it("round-trips a wall-clock time to the correct UTC instant", () => {
    // 12:00 Belgrade in summer == 10:00 UTC.
    const epoch = belgradeWallClockToEpoch("2026-07-15", "12:00");
    expect(new Date(epoch).toISOString()).toBe("2026-07-15T10:00:00.000Z");
  });
});
