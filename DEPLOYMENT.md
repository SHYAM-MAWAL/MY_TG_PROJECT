# Coolify Deployment Guide

## Production Readiness Checklist

✅ **Code Quality**
- Error handling implemented
- Graceful failure recovery
- No hardcoded credentials
- Environment variables properly used

✅ **Docker Support**
- Dockerfile created
- .dockerignore configured
- Session files persisted via volumes

✅ **Production Features**
- Continuous loop with error recovery
- Proper logging
- Duplicate prevention
- Status field with default value

## Deployment Steps

### 1. Prepare Your Repository

Ensure all files are committed:
- `main.py`
- `airtable_handler.py`
- `auth_telegram.py`
- `requirements.txt`
- `Dockerfile`
- `.dockerignore`

### 2. Configure Coolify

1. **Create New Application in Coolify**
   - Choose "Docker Compose" or "Dockerfile"
   - Connect your Git repository

2. **Set Environment Variables**
   Add these in Coolify's environment variables section:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE=+1234567890
   TELEGRAM_GROUP=your_group_username
   AIRTABLE_TOKEN=your_token
   AIRTABLE_BASE_ID=your_base_id
   AIRTABLE_TABLE=your_table_name
   SESSION_PATH=/app/sessions/session_name
   ```

3. **Configure Persistent Storage**
   - Mount volume: `/app/sessions` (for Telegram session files)
   - This ensures authentication persists across restarts

### 3. First-Time Authentication

**Option A: Using Coolify Terminal**
1. Deploy the application
2. Open terminal/console in Coolify
3. Run: `python auth_telegram.py --code YOUR_CODE`
4. Session will be saved to `/app/sessions/`

**Option B: Using Environment Variables**
Set these temporarily for first run:
```
TELEGRAM_CODE=your_verification_code
TELEGRAM_PASSWORD=your_2fa_password (if needed)
```

### 4. Deploy

1. Push your code to Git
2. Coolify will automatically build and deploy
3. Check logs to verify it's running
4. The scraper will run every 5 minutes automatically

## Production Considerations

### Session Persistence
- Session files are stored in `/app/sessions/` volume
- This volume persists across container restarts
- **Important**: Backup this volume for disaster recovery

### Monitoring
- Check Coolify logs regularly
- Monitor Airtable for new records
- Set up alerts for repeated failures

### Updates
- Push code changes to trigger rebuild
- Session files persist, so re-authentication not needed
- Environment variables can be updated without rebuild

### Scaling
- **Do NOT scale horizontally** (multiple instances)
- Telegram session files are single-instance
- Run only one container instance

### Health Checks
- Container health check configured
- Restarts automatically on failure
- Check logs if container keeps restarting

## Troubleshooting

### Container Keeps Restarting
1. Check logs: `docker logs <container_id>`
2. Verify environment variables are set
3. Check if session file is corrupted

### Authentication Issues
1. Delete session files: `rm /app/sessions/session_name.session*`
2. Re-authenticate using terminal
3. Restart container

### Airtable Connection Failed
1. Verify `AIRTABLE_TOKEN`, `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE`
2. Check Airtable API rate limits
3. Verify table field names match code

### No Courses Being Found
1. Check `TELEGRAM_GROUP` is correct
2. Verify bot has access to the group
3. Check Telegram API limits

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_API_ID` | Yes | Telegram API ID (integer) |
| `TELEGRAM_API_HASH` | Yes | Telegram API hash |
| `TELEGRAM_PHONE` | Yes | Phone number with country code |
| `TELEGRAM_GROUP` | Yes | Group username or ID |
| `AIRTABLE_TOKEN` | Yes | Airtable personal access token |
| `AIRTABLE_BASE_ID` | Yes | Airtable base ID |
| `AIRTABLE_TABLE` | Yes | Airtable table name |
| `SESSION_PATH` | No | Session file path (default: `/app/sessions/session_name`) |
| `TELEGRAM_CODE` | No | Verification code (first run only) |
| `TELEGRAM_PASSWORD` | No | 2FA password (if enabled) |

## Backup Strategy

1. **Session Files**: Backup `/app/sessions/` volume regularly
2. **Airtable**: All data is in Airtable (primary storage)
3. **Code**: Git repository serves as code backup

## Security Notes

- Never commit `.env` files
- Use Coolify's secret management for credentials
- Rotate Airtable tokens periodically
- Keep Telegram session files secure
