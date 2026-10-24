# Telegram Code Authentication Guide

## ⚠️ Important: Telegram Codes Expire Quickly!

Telegram verification codes:
- **Expire within 5 minutes** (sometimes faster)
- **Can only be used ONCE**
- **Rate limit after 3 failed attempts** (10-15 minute cooldown)

## 🔄 The Problem

If you set `TELEGRAM_CODE` in Coolify and leave it there:
- The script tries to use the same code every 5 minutes
- The code expires quickly
- After 3 failed attempts, Telegram blocks authentication for 10-15 minutes
- The script keeps retrying with the expired code, making it worse

## ✅ Solution: One-Time Code Usage

### Step 1: Request a Fresh Code

1. **Wait for the script to attempt authentication** (it will request a code automatically)
2. **Check your Telegram app** - you'll receive a new 5-6 digit code
3. **The code is valid for only a few minutes** - use it immediately!

### Step 2: Add Code to Coolify (Temporarily)

1. Go to **Coolify** → Your Application → **Environment Variables**
2. Add or update:
   - **Name**: `TELEGRAM_CODE`
   - **Value**: `12345` (your fresh code from Telegram)
3. **Save** the variable

### Step 3: Restart Container

1. **Restart** the container/application in Coolify
2. Check **Logs** - you should see:
   ```
   ✓ Using code from environment variable
   ✓ Authentication successful!
   ✓ Session saved. You can now run without authentication.
   ```

### Step 4: Remove Code Variable (IMPORTANT!)

**After successful authentication:**
1. Go back to **Environment Variables**
2. **Delete** the `TELEGRAM_CODE` variable
3. **Restart** the container

**Why?** 
- The code is only needed once
- After authentication, the session file is saved
- Leaving the code there causes it to be reused (and fail)

## 🚨 If You're Rate Limited

If you see this error:
```
⚠ RATE LIMITED - Too many failed authentication attempts
```

**What to do:**
1. **Wait 10-15 minutes** for the rate limit to reset
2. **Remove** `TELEGRAM_CODE` from environment variables
3. **Restart** the container (this will request a new code)
4. **Check Telegram** for the new code
5. **Add** the new code to `TELEGRAM_CODE` variable
6. **Restart** again to authenticate

## 📝 Best Practice Workflow

```
1. Script runs → Detects no session → Requests code
2. Check Telegram app → Get fresh code
3. Add TELEGRAM_CODE=your_code to Coolify
4. Restart container → Authentication succeeds
5. Remove TELEGRAM_CODE variable
6. Restart container (optional, but recommended)
7. Done! Session is saved, no more codes needed
```

## 🔍 How to Know if Authentication Worked

Look for these messages in logs:
```
✓ Authentication successful!
✓ Session saved. You can now run without authentication.
✓ Connected using existing session
Scanning messages for studybullet.com URLs...
```

If you see these, authentication is complete and you can remove `TELEGRAM_CODE`.

## ⚡ Quick Fix for Current Issue

If you're currently rate limited:

1. **Stop the container** (or wait 15 minutes)
2. **Delete** `TELEGRAM_CODE` from environment variables
3. **Delete** the session file (via terminal or restart with clean volume)
4. **Restart** container → It will request a new code
5. **Add** the new code to `TELEGRAM_CODE`
6. **Restart** again → Should authenticate successfully
7. **Remove** `TELEGRAM_CODE` after success

## 💡 Pro Tips

- **Don't leave `TELEGRAM_CODE` in environment variables** after authentication
- **Codes expire in minutes** - use them immediately
- **One code = one use** - don't reuse expired codes
- **Session files persist** - once authenticated, you don't need codes anymore
- **Check logs regularly** to catch authentication issues early

---

**Remember**: Telegram codes are temporary. Use them once, then remove the variable!
