# CLAUDE.md — Takvimi (Kosovo Prayer Times)

## Project overview
A bilingual (Albanian primary, English secondary) web app showing **official Kosovo prayer
times** with a live countdown to the next prayer, an Azan announcement, an Islamic-calendar
events page, and a Qibla compass. Login-free: there are **no user accounts**. The database
stores the official takvim data itself, not user data.

Authority / source of truth: **Bashkësia Islame e Kosovës (BIK)** — bislame.net and
dituriaislame.com. The app must reproduce BIK's published times exactly.

## Tech stack
- Backend: Python 3.12+, FastAPI (async), SQLAlchemy 2.0 (async), Alembic, Pydantic v2.
- Database: PostgreSQL.
- Frontend: React + TypeScript (strict), Vite, react-i18next, TanStack Query.
- Infra: Docker + docker-compose. Git for version control.

## Repository layout
```
takvimi/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/         # config (pydantic-settings), db session
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # prayer-time calc, qibla, events logic
│   │   └── data/         # seed.py, validate_against_bik.py, cities + events data
│   ├── alembic/
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/{components,pages,api,i18n,hooks}/
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── CLAUDE.md
```

## Data model
- `cities`: id, slug, name_sq, name_en, latitude, longitude, region (kosova|lugina), is_active.
- `prayer_times`: id, city_id (FK), date, imsak, sunrise, dhuhr, asr, maghrib, isha.
  Unique constraint on (city_id, date). Times stored as local Kosovo wall-clock time.
- `islamic_events`: id, date, hijri_label, name_sq, name_en, type (day|night|holiday),
  description_sq, description_en.

## API endpoints (all under /api)
- `GET /cities` — list active cities.
- `GET /prayer-times/today?city={slug}` — today's six times for a city.
- `GET /prayer-times?city={slug}&date=YYYY-MM-DD`
- `GET /prayer-times/month?city={slug}&year=&month=`
- `GET /prayer-times/year?city={slug}&year=`
- `GET /events?year=` — all events for the year.
- `GET /events/today` — the event for today, or null.
- `GET /qibla?city={slug}` — Qibla bearing in degrees from that city.

## Domain knowledge (critical — get this right)

### Albanian prayer names (official BIK terms)
| Albanian | Standard | Notes |
|---|---|---|
| Sabahu / Imsaku | Fajr | Dawn. BIK's published "Sabahu" = the imsak value (dawn-prayer time) |
| Lindja e Diellit | Sunrise | Not a prayer; display only; ends Fajr |
| Dreka | Dhuhr | Noon |
| Ikindia | Asr | **Standard (factor-1) Asr** — BIK publishes the BIM Kosovo / Diyanet method, NOT Hanafi factor-2 |
| Akshami | Maghrib | Sunset |
| Jacia | Isha | Night |
| Gjatësia e ditës | Length of day | sunset − sunrise; display only |

### Live countdown + Azan behavior (exact spec)
1. Compute the next upcoming prayer from today's times; after Jacia, target tomorrow's Sabahu.
2. Show a live HH:MM:SS countdown to that prayer, ticking every second.
3. **Base the countdown on Europe/Belgrade local time, NOT the user's device timezone** — the
   app shows Kosovo times, so it must stay correct for users abroad.
4. When the countdown hits 00:00:00: display "Koha e Ezanit" (sq) / "Time for Azan" (en) for
   the prayer that just entered, and hold it for **60 seconds**.
5. After 60 seconds, switch the target to the next prayer and resume the countdown.

### Today's-event banner
On the prayer page, if today matches an `islamic_events` date, show a banner:
"Sot është: {name_sq}" / "Today is: {name_en}". Otherwise show nothing.

### Qibla
Great-circle initial bearing from the city's (lat, lng) to the Kaaba (21.4225, 39.8262).
Qibla page uses the Device Orientation API + this bearing for a compass needle.

### Official events to seed (2026 / 1447–1448 H, from BIK)
Night of Mi'raj — 2026-01-15 · Mid-Sha'ban (Berat) — 2026-02-02 · Eve of Ramadan —
2026-02-18 · First day of Ramadan — 2026-02-19 · Night of Qadr — 2026-03-16 · Eve of Eid
al-Fitr — 2026-03-19 · Eid al-Fitr (Fitër Bajrami) — 2026-03-20 · Eve of Eid al-Adha —
2026-05-26 · Eid al-Adha (Kurban Bajrami) — 2026-05-27 · Islamic New Year 1448 — 2026-06-16 ·
Ashura — 2026-06-25 · Mawlid (Mevludi) — 2026-08-25 · Night of Ragha'ib — 2026-12-10.
(Store Albanian official names too: Nata e Miraxhit, Nata e Beratit, etc.)

### Cities
Seed the official Kosovo municipalities plus Lugina (Preševo Valley). Primary set: Prishtinë,
Prizren, Pejë, Gjakovë, Gjilan, Ferizaj, Mitrovicë, Vushtrri, Podujevë, Suharekë, Rahovec,
Lipjan, Kaçanik, Dragash, Deçan, Istog, Klinë, Skenderaj, Kamenicë, Viti — plus Lugina:
Preshevë, Bujanoc, Medvegjë. Coordinates live in `backend/app/data/cities.json`. Default
selected city: Prishtinë.

## Data sourcing & validation (non-negotiable)
- The app is seeded **directly from BIK's officially published takvim**: a committed Kosovo
  reference table (`backend/app/data/bik_takvim_2026.json`, from the official BIK /
  dituriaislame.com PDF) plus per-city minute offsets (`city_offsets.json`). This reproduces
  bislame.net **to the minute**. Method: BIM Kosovo — Fajr 18°, Isha 17°, 6-min temkin,
  standard (factor-1) Asr.
- City offsets: official BIK values where published (Prishtinë −1, Ferizaj/Gjilan/Podujevë/
  Vushtrri −1, Preshevë −2); the rest are derived from longitude via BIK's documented ~4 min/°
  rule (within the temkin margin) and refined if BIK publishes official values.
- `backend/app/data/validate_against_bik.py` asserts the seeded Prishtinë times match the
  official sampled dates in `bik_reference.json` **to the minute**. CI/test fails on any mismatch.
- The astronomical engine (`app/services/prayer_calc.py`) is a documented **fallback**, not the
  source of served times.
- Seed once into Postgres; the app serves from the DB. **Never call an external API at request
  time.** **Never present unvalidated times as official.**

## Conventions
- Python: full type hints; async throughout; ruff + black; pytest. Config via pydantic-settings.
- TypeScript: `strict` on, no `any`; function components + hooks; data via TanStack Query.
- i18n: Albanian (`sq`) is the source language and default; English (`en`) must be complete.
  No user-facing string is hardcoded — everything goes through i18n keys.
- Generate frontend API types from the FastAPI OpenAPI schema (`npm run gen:api`) so the
  frontend and backend contract never drift.
- Git: conventional commits; feature branches; never commit `.env` or secrets.
- Leave code formatting to the linters/formatters above — don't hand-format.

## Commands
- `docker compose up --build` — run the whole stack.
- Backend: `uvicorn app.main:app --reload` · `alembic upgrade head` · `pytest`
- Seed data: `python -m app.data.seed`
- Validate times vs BIK: `python -m app.data.validate_against_bik`
- Frontend: `npm run dev` · `npm run build` · `npm run gen:api`

## Immutable rules
1. Prayer-time accuracy is sacred — if unsure, flag it; never guess a time.
2. Serve times/events from Postgres, not a live third-party call.
3. Albanian first; English complete; no hardcoded UI strings.
4. No authentication, no accounts, no notifications — out of scope; do not add them.
5. All "today/now" logic uses Europe/Belgrade local time.

## MVP definition of done
City selector · prayer page (live clock, six times, countdown + Azan banner, today's-event
banner, sq/en toggle) · calendar page (month + year tables) · events page (full list, today
highlighted) · Qibla compass · times validated against BIK · events seeded · fully dockerized.
