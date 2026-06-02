import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

import en from "./en.json";
import sq from "./sq.json";

// Albanian (sq) is the source language and the default fallback (Immutable rule #3).
export const SUPPORTED_LANGUAGES = ["sq", "en"] as const;
export type Language = (typeof SUPPORTED_LANGUAGES)[number];

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      sq: { translation: sq },
      en: { translation: en },
    },
    fallbackLng: "sq",
    supportedLngs: SUPPORTED_LANGUAGES,
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      caches: ["localStorage"],
    },
  });

export default i18n;
