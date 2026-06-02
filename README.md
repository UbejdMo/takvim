# Takvimi — Kosovo Prayer Times

A bilingual (Albanian / English) web app showing the **official Kosovo prayer times** as
published by the **Bashkësia Islame e Kosovës (BIK)**, with a live countdown to the next
prayer, an Azan announcement, an Islamic-calendar events page, and a Qibla compass.

There are **no user accounts** and **no authentication** — the database stores the official
takvim data, not user data.

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- API docs (Swagger): http://localhost:8000/docs

The backend container runs migrations, seeds the official takvim into Postgres, then serves.

## Local development

### Backend
```bash
cd backend
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
alembic upgrade head
python -m app.data.seed
uvicorn app.main:app --reload
pytest
```

### Frontend
```bash
cd frontend
npm install
npm run gen:api      # regenerate API types from the backend OpenAPI schema
npm run dev
```

## Architecture

- **Backend** — Python 3.12+, FastAPI (async), SQLAlchemy 2.0 (async), Alembic, Pydantic v2,
  PostgreSQL.
- **Frontend** — React + TypeScript (strict), Vite, react-i18next, TanStack Query.

Prayer times are produced by an astronomical calculation engine (`app/services/prayer_calc.py`)
configured to reproduce BIK's published times: **Hanafi Asr**, Balkan/Diyanet-style Fajr–Isha
twilight angles, plus per-prayer minute offsets (*ihtiyat*). Times are computed once and
**seeded into Postgres** — the app never calls an external service at request time.

## Non-negotiable rules

1. Prayer-time accuracy is sacred. `python -m app.data.validate_against_bik` checks the
   generated Prishtinë times against BIK's published takvim for sample dates across the year;
   **never present uncalibrated/unvalidated times as official.**
2. Times and events are served from Postgres, never a live third-party call.
3. Albanian first; English complete; no hardcoded UI strings (everything via i18n).
4. No authentication, accounts, or notifications — out of scope.
5. All "today / now" logic uses **Europe/Belgrade** local time.

## Project layout

```
backend/   FastAPI app, calc engine, seed + validation data, Alembic, tests
frontend/  React + Vite SPA (prayer page, calendar, events, Qibla)
docker-compose.yml
.env.example
```
