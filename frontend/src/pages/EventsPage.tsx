import { useTranslation } from "react-i18next";

import { ErrorBox, Loading } from "../components/Status";
import { useEvents } from "../hooks/useApi";
import { belgradeToday } from "../lib/belgrade";
import { dayMonth } from "../lib/time";

/** Full list of this year's Islamic events; today's event is outlined in gold. */
export default function EventsPage() {
  const { t, i18n } = useTranslation();
  const todayIso = belgradeToday();
  const year = Number(todayIso.slice(0, 4));
  const { data, isLoading, isError } = useEvents(year);

  const lang = i18n.language.startsWith("en") ? "en" : "sq";

  return (
    <>
      <h2>{t("events.title")}</h2>
      {isLoading && <Loading />}
      {isError && <ErrorBox />}
      {data && data.length === 0 && <p className="muted center">{t("events.none")}</p>}
      {data?.map((event) => {
        const name = lang === "en" ? event.name_en : event.name_sq;
        const description = lang === "en" ? event.description_en : event.description_sq;
        const isToday = event.date === todayIso;
        return (
          <div className="card" key={event.date}>
            <div className={`event-item${isToday ? " today" : ""}`}>
              <div>
                <strong>{name}</strong>
                <div className="muted">
                  {event.hijri_label}
                  {description ? ` · ${description}` : ""}
                </div>
              </div>
              <div className="center">
                <span className="badge">{t(`events.type.${event.type}`)}</span>
                <div className="muted">{dayMonth(event.date)}</div>
              </div>
            </div>
          </div>
        );
      })}
    </>
  );
}
