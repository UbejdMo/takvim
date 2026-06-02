import { useTranslation } from "react-i18next";

import { SUPPORTED_LANGUAGES } from "../i18n";

/** sq/en toggle. Albanian is the default; English must stay complete (Immutable rule #3). */
export function LanguageToggle() {
  const { t, i18n } = useTranslation();
  const current = i18n.language.startsWith("en") ? "en" : "sq";

  const change = (lng: string) => {
    void i18n.changeLanguage(lng);
    document.documentElement.lang = lng;
  };

  return (
    <div className="lang-toggle controls" role="group" aria-label={t("language.toggle")}>
      {SUPPORTED_LANGUAGES.map((lng) => (
        <button
          key={lng}
          type="button"
          className={current === lng ? "active" : ""}
          aria-pressed={current === lng}
          onClick={() => change(lng)}
        >
          {t(`language.${lng}`)}
        </button>
      ))}
    </div>
  );
}
