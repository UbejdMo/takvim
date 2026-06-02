import { useTranslation } from "react-i18next";

/** Centered "loading…" line, shared by every page that waits on a query. */
export function Loading() {
  const { t } = useTranslation();
  return <p className="muted center">{t("common.loading")}</p>;
}

/**
 * Centered error line. `messageKey` lets a page distinguish a generic failure from a
 * "not seeded for this date" 404 (CLAUDE.md: never present a missing date as a real time).
 */
export function ErrorBox({ messageKey = "common.error" }: { messageKey?: string }) {
  const { t } = useTranslation();
  return <p className="error center">{t(messageKey)}</p>;
}
