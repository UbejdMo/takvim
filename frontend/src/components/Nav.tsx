import { useTranslation } from "react-i18next";
import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", key: "prayer", end: true },
  { to: "/kalendari", key: "calendar", end: false },
  { to: "/ngjarjet", key: "events", end: false },
  { to: "/kibla", key: "qibla", end: false },
] as const;

/** Top-level page navigation; the active route gets the accent pill (styles.css `.nav a.active`). */
export function Nav() {
  const { t } = useTranslation();
  return (
    <nav className="nav">
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          end={link.end}
          className={({ isActive }) => (isActive ? "active" : "")}
        >
          {t(`nav.${link.key}`)}
        </NavLink>
      ))}
    </nav>
  );
}
