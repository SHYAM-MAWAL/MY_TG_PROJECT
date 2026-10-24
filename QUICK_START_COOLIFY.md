# Deploy to Coolify (current stack)

You deploy **two things** from this repo via Docker Compose:

1. `telegram-scraper` — Telegram → Postgres  
2. `courses-api` — `GET /courses` for https://courses.shyamai.in/

The **frontend** (`frontend/`) is separate (Cloudflare Pages / static). Point it at the public API URL after deploy.

---

## 1. Push code to GitHub

```bash
cd /Users/sham/VSCode/MY_TG_PROJECT
git status
git add .
git commit -m "Coolify: scraper + courses API on Postgres"
git push origin main
```

Do **not** commit `.env` (already gitignored). Set secrets in Coolify.

---

## 2. Create app in Coolify

1. **New Resource** → **Application**
2. Connect GitHub repo: `SHYAM-MAWAL/MY_TG_PROJECT`
3. **Build Pack**: **Docker Compose**
4. Compose file: `docker-compose.yaml`
5. Branch: `main`

---

## 3. Environment variables (Coolify UI)

Use the **internal** Postgres host (same Coolify server):

```
TELEGRAM_API_ID=...
TELEGRAM_API_HASH=...
TELEGRAM_PHONE=+91...
TELEGRAM_GROUP=freshercooker_official

POSTGRES_HOST=ehl6emvbhq43ifzrvmxowu49
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=...
POSTGRES_DB=postgres
POSTGRES_SSLMODE=disable

COURSE_PURGE_DAYS=3
SESSION_PATH=/app/sessions/session_name
PORT=8080
```

> Local Mac used `185.245.182.223:5433`. On Coolify use **internal** `ehl6emvbhq43ifzrvmxowu49:5432`.

---

## 4. Persistent volume (required)

For `telegram-scraper` service:

| Mount path       | Purpose              |
|------------------|----------------------|
| `/app/sessions`  | Telegram login session |

Without this, every redeploy needs re-login.

---

## 5. Domain for courses-api

1. In Coolify, open **courses-api** service  
2. Add a domain, e.g. `courses-api.shyamai.in`  
3. Port: **8080**  
4. Enable HTTPS  

Test after deploy:

```bash
curl https://courses-api.shyamai.in/health
curl https://courses-api.shyamai.in/courses?limit=2
```

---

## 6. Deploy

Click **Deploy**. Wait for both services to become healthy.

---

## 7. Telegram auth (one time)

Session must live in `/app/sessions`.

**Easiest on Coolify:**

1. Open scraper **Terminal**
2. Run QR login (if available) or:
   ```bash
   python auth_telegram.py
   ```
3. Or set temporary env `TELEGRAM_CODE=12345`, restart scraper once, then **remove** `TELEGRAM_CODE`

Logs should show:

```
✓ Postgres connected
✓ Connected to: ...
Scanning messages...
✓ Inserted into Postgres
```

---

## 8. Point frontend at the API

In `frontend/.env.local` / Cloudflare Pages env:

```
NEXT_PUBLIC_COURSES_API_URL=https://courses-api.shyamai.in
```

Rebuild & deploy the frontend (Cloudflare Pages / `SHYAMAI_Web`).

Then https://courses.shyamai.in/ loads courses from your Coolify Postgres API.

---

## Checklist

- [ ] Code pushed to GitHub  
- [ ] Coolify app = Docker Compose  
- [ ] Env vars set (internal Postgres)  
- [ ] Volume `/app/sessions`  
- [ ] Domain on `courses-api` :8080  
- [ ] Telegram session authenticated  
- [ ] Frontend `NEXT_PUBLIC_COURSES_API_URL` updated & redeployed  

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Postgres connection refused | Use internal host/port `5432`, not external `5433` |
| Auth loop | Persist `/app/sessions`; remove stale `TELEGRAM_CODE` |
| API 502 | Check `courses-api` logs; domain → port 8080 |
| Site empty | Set frontend `NEXT_PUBLIC_COURSES_API_URL` to your API domain and redeploy UI |
| Single scraper only | Don’t scale scraper horizontally (one Telegram session) |
