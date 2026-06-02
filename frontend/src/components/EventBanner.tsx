import { useTranslation } from "react-i18next";

import { useEventToday } from "../hooks/useApi";

/** Golden banner shown only when today (Europe/Belgrade) matches a seeded Islamic event. */
export function EventBanner() {
  const { t, i18n } = useTranslation();
  const { data: event } = useEventToday();

  if (!event) return null;

  const lang = i18n.language.startsWith("en") ? "en" : "sq";
  const name = lang === "en" ? event.name_en : event.name_sq;
  return <div className="event-banner">{t("eventBanner.today", { name })}</div>;
}
