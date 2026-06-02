import { useEffect, useMemo, useState } from "react";

import type { PrayerTimes } from "../api/types";
import { nextDay } from "../lib/belgrade";
import { type CountdownState, buildTargets, computeCountdown } from "../lib/countdown";

/**
 * Live countdown to the next prayer, ticking every second, anchored to Europe/Belgrade.
 * Needs today's times and tomorrow's Sabahu (imsak) so it can roll over after Jacia.
 */
export function useCountdown(
  today: PrayerTimes | undefined,
  tomorrowImsak: string | undefined,
): CountdownState | null {
  const targets = useMemo(() => {
    if (!today || !tomorrowImsak) return [];
    return buildTargets(today.date, today, nextDay(today.date), tomorrowImsak);
  }, [today, tomorrowImsak]);

  const [state, setState] = useState<CountdownState | null>(() =>
    computeCountdown(Date.now(), targets),
  );

  useEffect(() => {
    setState(computeCountdown(Date.now(), targets));
    if (targets.length === 0) return;
    const id = window.setInterval(() => {
      setState(computeCountdown(Date.now(), targets));
    }, 1000);
    return () => window.clearInterval(id);
  }, [targets]);

  return state;
}
