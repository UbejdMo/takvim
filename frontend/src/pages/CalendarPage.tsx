import { useState } from "react";
import { useTranslation } from "react-i18next";

import type { PrayerTimes } from "../api/types";
import { ErrorBox, Loading } from "../components/Status";
import { useMonth, useYear } from "../hooks/useApi";
import { belgradeToday } from "../lib/belgrade";
import { dayMonth, hhmm } from "../lib/time";

/** Time columns shown in the calendar tables (sunrise included; it's part of BIK's takvim). */
const COLUMNS = ["imsak", "sunrise", "dhuhr", "asr", "maghrib", "isha"] as const;

/** Presentational table of daily times; today's row is highlighted (styles.css `tr.today`). */
function TimesTable({ rows, todayIso }: { rows: PrayerTimes[]; todayIso: string }) {
  const { t } = useTranslation();
  if (rows.length === 0) return <ErrorBox messageKey="common.notSeeded" />;

  return (
    <div className="card">
      <table>
        <thead>
          <tr>
            <th>{t("calendar.date")}</th>
            {COLUMNS.map((key) => (
              <th key={key}>{t(`prayers.${key}`)}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.date} className={row.date === todayIso ? "today" : ""}>
              <td>{dayMonth(row.date)}</td>
              {COLUMNS.map((key) => (
                <td key={key}>{hhmm(row[key])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MonthTable({
  city,
  year,
  month,
  todayIso,
}: {
  city: string;
  year: number;
  month: number;
  todayIso: string;
}) {
  const { data, isLoading, isError } = useMonth(city, year, month);
  if (isLoading) return <Loading />;
  if (isError || !data) return <ErrorBox />;
  return <TimesTable rows={data} todayIso={todayIso} />;
}

function YearTable({
  city,
  year,
  todayIso,
}: {
  city: string;
  year: number;
  todayIso: string;
}) {
  const { data, isLoading, isError } = useYear(city, year);
  if (isLoading) return <Loading />;
  if (isError || !data) return <ErrorBox />;
  return <TimesTable rows={data} todayIso={todayIso} />;
}

/**
 * Calendar page: a month or a full-year table of prayer times for the selected city.
 * The inactive view stays unmounted so only the chosen month/year query runs.
 */
export default function CalendarPage({ city }: { city: string }) {
  const { t } = useTranslation();
  const todayIso = belgradeToday();
  const todayYear = Number(todayIso.slice(0, 4));
  const todayMonth = Number(todayIso.slice(5, 7));

  const [view, setView] = useState<"month" | "year">("month");
  const [year, setYear] = useState(todayYear);
  const [month, setMonth] = useState(todayMonth);

  return (
    <>
      <h2>{t("calendar.title")}</h2>
      <div className="card controls">
        <div className="lang-toggle">
          <button
            type="button"
            className={view === "month" ? "active" : ""}
            onClick={() => setView("month")}
          >
            {t("calendar.monthView")}
          </button>
          <button
            type="button"
            className={view === "year" ? "active" : ""}
            onClick={() => setView("year")}
          >
            {t("calendar.yearView")}
          </button>
        </div>

        {view === "month" && (
          <select
            aria-label={t("calendar.monthView")}
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
          >
            {Array.from({ length: 12 }, (_, i) => (
              <option key={i} value={i + 1}>
                {t(`calendar.months.${i}`)}
              </option>
            ))}
          </select>
        )}

        <select
          aria-label={t("calendar.yearView")}
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
        >
          {[todayYear, todayYear + 1].map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {view === "month" ? (
        <MonthTable city={city} year={year} month={month} todayIso={todayIso} />
      ) : (
        <YearTable city={city} year={year} todayIso={todayIso} />
      )}
    </>
  );
}
