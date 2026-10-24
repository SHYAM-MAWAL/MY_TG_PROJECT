# Coolify Authentication Guide

## 🔐 Problem: Session Expired or Invalid

If you see this error in logs:
```
⚠ Session expired or invalid. Re-authentication required.
✗ Authentication cancelled. Cannot proceed without code.
```

This means your Telegram session has expired and needs to be re-authenticated.

## ✅ Solution: Authenticate Using Environment Variable

### Step 1: Get Verification Code from Telegram

1. Open your **Telegram app** on your phone
2. You should receive a **verification code** (5-6 digits)
3. If you don't see it, you can request a new one:
   - The script will automatically request one when it tries to authenticate
   - Or go to Telegram Settings → Privacy → Active Sessions

### Step 2: Add Code to Coolify Environment Variables

1. **Go to Coolify** → Your Application → **Configuration** → **Environment Variables**
2. **Click "Add Variable"**
3. Add this temporary variable:
   - **Name**: `TELEGRAM_CODE`
   - **Value**: `12345` (your actual code from Telegram)
   - **Example**: If Telegram sent `28104`, set value to `28104`

### Step 3: Restart Container

1. **Save** the environment variable
2. **Restart** the container/application
3. Check **Logs** - you should see:
   ```
   ✓ Using code from environment variable
   ✓ Authentication successful!
   ✓ Session saved. You can now run without authentication.
   ```

### Step 4: Remove Temporary Code (Important!)

**After successful authentication:**
1. Go back to **Environment Variables**
2. **Delete** the `TELEGRAM_CODE` variable
3. **Restart** the container

**Why?** The code is only needed once. After authentication, the session file is saved and you don't need the code anymore.

## 🔄 If You Have 2FA Enabled

If your Telegram account has 2FA (Two-Factor Authentication):

1. Add both variables:
   - `TELEGRAM_CODE` = your verification code
   - `TELEGRAM_PASSWORD` = your 2FA password
2. Restart container
3. After successful authentication, remove both variables

## 🐛 Troubleshooting

### Code Not Working
- **Problem**: Code expired (they expire quickly, usually within 5 minutes)
- **Solution**: Request a new code from Telegram and update `TELEGRAM_CODE` immediately

### Still Getting Errors
- **Problem**: Invalid session file
- **Solution**: The script now automatically deletes invalid session files. Just add `TELEGRAM_CODE` and restart.

### Container Keeps Restarting
- **Problem**: Authentication keeps failing
- **Solution**: 
  1. Make sure `TELEGRAM_CODE` is set correctly (no spaces, just the numbers)
  2. Request a fresh code from Telegram
  3. Update the variable and restart immediately

### Authentication Successful But Still Failing
- **Problem**: Session file not persisting
- **Solution**: 
  1. Check **Persistent Storage** is configured for `/app/sessions`
  2. Verify the volume is mounted correctly
  3. Check logs for volume mount errors

## 📝 Quick Steps Summary

```
1. Get code from Telegram app
2. Add TELEGRAM_CODE=your_code in Coolify
3. Restart container
4. Wait for "✓ Authentication successful!"
5. Remove TELEGRAM_CODE variable
6. Restart container (optional, but recommended)
```

## ✅ Success Indicators

After successful authentication, you should see:
```
✓ Using code from environment variable
✓ Authentication successful!
✓ Session saved. You can now run without authentication.
💡 Tip: You can remove TELEGRAM_CODE from environment variables now.
✓ Connected using existing session
Scanning messages for studybullet.com URLs...
```

## 🔒 Security Note

- **Never commit** `TELEGRAM_CODE` to Git
- **Remove** the code variable after authentication
- The session file is stored in the persistent volume (secure)

---

**Need help?** Check the logs for specific error messages. The script now provides clear instructions on what to do.
