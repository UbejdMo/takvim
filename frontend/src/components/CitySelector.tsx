import { useTranslation } from "react-i18next";

import type { City } from "../api/types";
import { useCities } from "../hooks/useApi";

/** Region-grouped city dropdown. Names follow the active language (Albanian first). */
export function CitySelector({
  value,
  onChange,
}: {
  value: string;
  onChange: (slug: string) => void;
}) {
  const { t, i18n } = useTranslation();
  const { data: cities } = useCities();

  const lang = i18n.language.startsWith("en") ? "en" : "sq";
  const label = (c: City) => (lang === "en" ? c.name_en : c.name_sq);

  const kosova = cities?.filter((c) => c.region === "kosova") ?? [];
  const lugina = cities?.filter((c) => c.region === "lugina") ?? [];

  return (
    <select
      aria-label={t("city.select")}
      value={value}
      onChange={(e) => onChange(e.target.value)}
    >
      <optgroup label={t("city.regionKosova")}>
        {kosova.map((c) => (
          <option key={c.slug} value={c.slug}>
            {label(c)}
          </option>
        ))}
      </optgroup>
      {lugina.length > 0 && (
        <optgroup label={t("city.regionLugina")}>
          {lugina.map((c) => (
            <option key={c.slug} value={c.slug}>
              {label(c)}
            </option>
          ))}
        </optgroup>
      )}
    </select>
  );
}
