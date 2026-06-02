import { useTranslation } from "react-i18next";

import { type CountdownState, formatHMS } from "../lib/countdown";

/**
 * Live countdown card. In the "azan" phase it switches to the accent banner showing
 * "Koha e Ezanit" / "Time for Azan" for the prayer that just entered (held 60s by the hook).
 */
export function Countdown({ state }: { state: CountdownState | null }) {
  const { t } = useTranslation();
  if (!state) return null;

  if (state.phase === "azan") {
    return (
      <div className="card countdown azan">
        <div className="next-name">{t(`prayers.${state.key}`)}</div>
        <div className="azan-text">{t("azan.now")}</div>
      </div>
    );
  }

  return (
    <div className="card countdown">
      <div className="label">{t("countdown.next")}</div>
      <div className="next-name">{t(`prayers.${state.key}`)}</div>
      <div className="clock">{formatHMS(state.msRemaining)}</div>
    </div>
  );
}
