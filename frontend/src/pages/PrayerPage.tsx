import { useTranslation } from "react-i18next";

import type { PrayerTimes } from "../api/types";
import { Countdown } from "../components/Countdown";
import { EventBanner } from "../components/EventBanner";
import { ErrorBox, Loading } from "../components/Status";
import { useTimesOnDate, useTodayTimes } from "../hooks/useApi";
import { useCountdown } from "../hooks/useCountdown";
import { belgradeToday, nextDay } from "../lib/belgrade";
import { dayLength, hhmm } from "../lib/time";

/** Rows shown on the prayer page, in display order. Sunrise is display-only (not a prayer). */
const DISPLAY_ORDER = ["imsak", "sunrise", "dhuhr", "asr", "maghrib", "isha"] as const;

/**
 * Main page: today's-event banner, the live countdown + Azan announcement, and the six daily
 * times with the upcoming prayer highlighted. Everything is anchored to Europe/Belgrade.
 */
export default function PrayerPage({ city }: { city: string }) {
  const { t } = useTranslation();
  const today = useTodayTimes(city);

  // Tomorrow's Sabahu lets the countdown roll over after Jacia.
  const tomorrow = useTimesOnDate(city, nextDay(belgradeToday()));
  const state = useCountdown(today.data, tomorrow.data?.imsak);

  if (today.isLoading) return <Loading />;
  if (today.isError || !today.data) {
    const notSeeded = today.error instanceof Error && today.error.message.includes("404");
    return <ErrorBox messageKey={notSeeded ? "common.notSeeded" : "common.error"} />;
  }

  const times: PrayerTimes = today.data;

  return (
    <>
      <EventBanner />
      <Countdown state={state} />
      <div className="card">
        <div className="times">
          {DISPLAY_ORDER.map((key) => (
            <div
              key={key}
              className={`time-row${state && state.key === key ? " next" : ""}`}
            >
              <span className="name">{t(`prayers.${key}`)}</span>
              <span className="value">{hhmm(times[key])}</span>
            </div>
          ))}
          <div className="time-row">
            <span className="name">{t("prayers.dayLength")}</span>
            <span className="value">{dayLength(times.sunrise, times.maghrib)}</span>
          </div>
        </div>
      </div>
    </>
  );
}
