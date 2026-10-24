# SHYAMAI Course Scraper

Telegram → StudyBullet → Udemy → **Postgres**, with a small HTTP API for the Learning Hub frontend.

**Repo:** https://github.com/SHYAM-MAWAL/MY_TG_PROJECT

## Architecture

```
Telegram group
  → main.py (scraper loop)
      → Postgres `courses` table
          → courses_api.py  (GET /courses)
              → frontend (Next.js) / Coolify domain
```

| Component | Role |
|-----------|------|
| `main.py` | Polls Telegram, extracts Udemy links, inserts into Postgres |
| `postgres_handler.py` | DB access + schema + 3-day auto-purge |
| `courses_api.py` | Public JSON API for the dashboard |
| `frontend/` | SHYAMAI Learning Hub UI |
| `auth_telegram.py` / `auth_telegram_qr.py` | One-time Telegram login |

## Features

- Incremental Telegram fetch (`last_message_id.txt`)
- StudyBullet URL cache (`seen_source_urls.txt`)
- Duplicate protection via unique `target_url`
- Auto-purge courses older than **3 days** (`COURSE_PURGE_DAYS`)
- Fast API list (images loaded lazily)
- Docker Compose for Coolify: scraper + API

## Requirements

- Python 3.10+
- Telegram API credentials ([my.telegram.org/apps](https://my.telegram.org/apps))
- Postgres (Coolify or local)
- Access to the target Telegram group/channel

## Local setup

```bash
git clone https://github.com/SHYAM-MAWAL/MY_TG_PROJECT.git
cd MY_TG_PROJECT
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env_template.txt .env   # fill in Telegram + Postgres
```

### Authenticate Telegram (once)

```bash
python auth_telegram_qr.py
# or: python auth_telegram.py
```

### Run scraper

```bash
python main.py
```

### Run courses API

```bash
python courses_api.py
# GET http://127.0.0.1:8080/health
# GET http://127.0.0.1:8080/courses?limit=20
```

### Run frontend

```bash
cd frontend
cp .env.local.example .env.local   # NEXT_PUBLIC_COURSES_API_URL=http://127.0.0.1:8080
npm install --legacy-peer-deps
npm run dev
```

## Environment variables

| Variable | Required | Notes |
|----------|----------|--------|
| `TELEGRAM_API_ID` | yes | From my.telegram.org |
| `TELEGRAM_API_HASH` | yes | |
| `TELEGRAM_PHONE` | yes | With country code, e.g. `+91...` |
| `TELEGRAM_GROUP` | yes | Username without `@` |
| `POSTGRES_HOST` | yes | Coolify internal hostname, or external IP |
| `POSTGRES_PORT` | yes | Internal `5432` / external often `5433` |
| `POSTGRES_USER` | yes | |
| `POSTGRES_PASSWORD` | yes | |
| `POSTGRES_DB` | yes | Usually `postgres` |
| `POSTGRES_SSLMODE` | no | `disable` for typical Coolify Postgres |
| `COURSE_PURGE_DAYS` | no | Default `3` |
| `SESSION_PATH` | no | Default `session_name` / `/app/sessions/...` in Docker |
| `PORT` | no | API port, default `8080` |

See `env_template.txt`.

## Coolify deploy

See **[QUICK_START_COOLIFY.md](QUICK_START_COOLIFY.md)** for step-by-step:

1. Connect this GitHub repo in Coolify (Docker Compose)
2. Set env vars (use **internal** Postgres host/port)
3. Persist volume `/app/sessions`
4. Expose `courses-api` on port `8080` with a domain
5. Authenticate Telegram once
6. Point frontend `NEXT_PUBLIC_COURSES_API_URL` at that API domain

## Postgres schema

Table `courses` (auto-created on connect):

- `id`, `course_title`, `target_url` (unique), `image`, `status`, `created_at`

SQL reference: `postgres_schema.sql`

## Project layout

```
├── main.py                 # Scraper loop
├── courses_api.py          # HTTP API
├── postgres_handler.py     # Postgres
├── auth_telegram.py        # Code login
├── auth_telegram_qr.py     # QR login
├── docker-compose.yaml     # scraper + courses-api
├── Dockerfile
├── env_template.txt
├── frontend/               # Next.js UI
└── QUICK_START_COOLIFY.md  # Deploy guide
```

## Security

- Never commit `.env` or `*.session`
- Rotate any tokens that were ever committed historically
- Use Coolify secrets for production credentials
