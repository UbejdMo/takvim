import { useTranslation } from "react-i18next";

import { CitySelector } from "./CitySelector";
import { LanguageToggle } from "./LanguageToggle";

/** App header: title + subtitle on the left, city selector and language toggle on the right. */
export function Header({
  city,
  onCityChange,
}: {
  city: string;
  onCityChange: (slug: string) => void;
}) {
  const { t } = useTranslation();
  return (
    <header className="header">
      <div>
        <h1>{t("app.title")}</h1>
        <div className="subtitle">{t("app.subtitle")}</div>
      </div>
      <div className="controls">
        <CitySelector value={city} onChange={onCityChange} />
        <LanguageToggle />
      </div>
    </header>
  );
}
