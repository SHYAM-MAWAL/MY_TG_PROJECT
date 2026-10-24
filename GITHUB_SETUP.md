# GitHub Setup & Coolify Deployment Guide

## 🚀 Step 1: Initialize Git Repository

If you haven't initialized Git yet, run these commands:

```bash
cd "C:\Cursor Projects\First Cursor project"
git init
git branch -M main
```

## 📤 Step 2: Add All Files to Git

```bash
git add .
```

**Note**: The `.gitignore` file will automatically exclude:
- `.env` files (your secrets)
- `*.session` files (Telegram authentication)
- `__pycache__/` directories
- Other sensitive/temporary files

## 💾 Step 3: Commit Your Code

```bash
git commit -m "Initial commit: Production-ready Telegram course scraper"
```

## 🔗 Step 4: Connect to GitHub Repository

```bash
git remote add origin https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy.git
```

If the repository already exists and you want to replace it:
```bash
git remote set-url origin https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy.git
```

## 📤 Step 5: Push to GitHub

```bash
git push -u origin main
```

If you get authentication errors, you may need to:
- Use a Personal Access Token instead of password
- Or use SSH: `git@github.com:SHYAM-MAWAL/SHYAMAI_Udemy.git`

## ✅ Step 6: Verify on GitHub

1. Go to: https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy
2. Verify all files are uploaded
3. **IMPORTANT**: Make sure `.env` and `*.session` files are NOT visible (they should be ignored)

## 🎯 Step 7: Deploy to Coolify

### Option A: Using Coolify UI

1. **Login to Coolify**
2. **Create New Application**
   - Choose "Docker Compose" or "Dockerfile"
3. **Connect GitHub Repository**
   - Click "Connect Repository"
   - Select: `https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy.git`
   - Choose branch: `main`
4. **Configure Build**
   - Build Pack: Auto-detect (should detect Python/Dockerfile)
   - Or manually select: Dockerfile
5. **Set Environment Variables**
   Add these in Coolify's environment variables:
   ```
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   TELEGRAM_PHONE=+1234567890
   TELEGRAM_GROUP=your_group_username
   AIRTABLE_TOKEN=your_token
   AIRTABLE_BASE_ID=your_base_id
   AIRTABLE_TABLE=your_table_name
   ```
6. **Configure Persistent Storage**
   - Add volume: `/app/sessions`
   - Name: `telegram-sessions`
   - This stores Telegram session files
7. **Deploy**
   - Click "Deploy" button
   - Wait for build to complete

### Option B: Using coolify.yaml (if supported)

If Coolify supports YAML configuration:
- The `coolify.yaml` file is already in the repository
- Coolify should auto-detect it
- You still need to set environment variables in the UI

## 🔐 Step 8: First-Time Authentication

After deployment, authenticate Telegram:

**Method 1: Using Coolify Terminal**
1. Open terminal/console in Coolify
2. Run: `python auth_telegram.py --code YOUR_CODE`
3. Enter verification code when prompted

**Method 2: Using Environment Variable**
1. Add temporary variable: `TELEGRAM_CODE=your_code`
2. Restart container
3. Remove variable after authentication

## ✅ Step 9: Verify Deployment

Check logs in Coolify - you should see:
```
✓ Airtable connected
✓ Found existing session file, attempting to connect...
✓ Connected using existing session
Scanning messages for studybullet.com URLs...
```

## 🔄 Step 10: Auto-Deploy (Optional)

Coolify can auto-deploy on Git push:
1. Go to application settings
2. Enable "Auto Deploy"
3. Select branch: `main`
4. Now every `git push` will trigger a new deployment

## 📝 Quick Command Reference

```bash
# Initialize (if needed)
git init
git branch -M main

# Add and commit
git add .
git commit -m "Your commit message"

# Connect to GitHub (first time)
git remote add origin https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy.git

# Push to GitHub
git push -u origin main

# Future updates
git add .
git commit -m "Update description"
git push
```

## ⚠️ Important Notes

1. **Never commit `.env` files** - They contain secrets
2. **Never commit `*.session` files** - They contain authentication tokens
3. **Always verify** `.gitignore` is working before pushing
4. **Backup session files** - They're stored in the volume, not in Git
5. **Single instance only** - Don't scale horizontally (Telegram limitation)

## 🐛 Troubleshooting

### Git Push Fails
- Check you have write access to the repository
- Verify repository URL is correct
- Try using Personal Access Token for authentication

### Coolify Can't Find Dockerfile
- Verify `Dockerfile` is in the root directory
- Check it's committed to Git
- Review build logs in Coolify

### Authentication Fails in Container
- Check environment variables are set correctly
- Verify volume mount for `/app/sessions`
- Use terminal to manually authenticate

### Container Keeps Restarting
- Check logs for error messages
- Verify all required environment variables are set
- Check Airtable credentials are correct

## 📚 Additional Resources

- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [QUICK_START_COOLIFY.md](QUICK_START_COOLIFY.md) - Quick deployment steps
- [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) - Production readiness

---

**Repository**: https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy.git
