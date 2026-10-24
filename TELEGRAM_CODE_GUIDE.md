# Telegram authentication notes

## Codes expire quickly

- Usually valid only a few minutes
- One-time use
- After several failures Telegram may rate-limit for 10–15 minutes

## Preferred: QR login

```bash
python auth_telegram_qr.py
```

Phone → Telegram → **Settings → Devices → Link Desktop Device** → scan QR.

## Alternative: SMS / in-app code

```bash
python auth_telegram.py
```

Codes often arrive **inside the Telegram app** (official Telegram chat), not as SMS.

## Coolify

1. Persist volume `/app/sessions`
2. Temporary env `TELEGRAM_CODE=12345` → restart scraper once
3. **Remove** `TELEGRAM_CODE` after success
4. Do not leave an expired code in env (causes retry loops)

## Session files

- Local: `session_name.session`
- Docker: `/app/sessions/session_name.session`

If auth fails repeatedly, delete the session file(s) and login again.
