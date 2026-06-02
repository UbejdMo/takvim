import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { Header } from "./components/Header";
import { Nav } from "./components/Nav";
import CalendarPage from "./pages/CalendarPage";
import EventsPage from "./pages/EventsPage";
import PrayerPage from "./pages/PrayerPage";
import QiblaPage from "./pages/QiblaPage";

const DEFAULT_CITY = "prishtine";
const CITY_STORAGE_KEY = "takvimi.city";

/**
 * App shell: holds the selected city (persisted to localStorage, default Prishtinë) and renders
 * the header, navigation, and routed pages. No accounts/auth — the only client state is the
 * chosen city and language (Immutable rule #4).
 */
export default function App() {
  const [city, setCity] = useState<string>(
    () => localStorage.getItem(CITY_STORAGE_KEY) ?? DEFAULT_CITY,
  );

  useEffect(() => {
    localStorage.setItem(CITY_STORAGE_KEY, city);
  }, [city]);

  return (
    <div className="app-shell">
      <Header city={city} onCityChange={setCity} />
      <Nav />
      <main>
        <Routes>
          <Route path="/" element={<PrayerPage city={city} />} />
          <Route path="/kalendari" element={<CalendarPage city={city} />} />
          <Route path="/ngjarjet" element={<EventsPage />} />
          <Route path="/kibla" element={<QiblaPage city={city} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
