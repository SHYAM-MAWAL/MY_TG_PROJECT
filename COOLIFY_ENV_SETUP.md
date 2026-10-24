# Coolify Environment Variables Setup

## ⚠️ Error: Environment Variables Not Set

If you're seeing this error:
```
TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
```

This means **environment variables are not configured** in Coolify.

## ✅ Solution: Set Environment Variables in Coolify

### Step 1: Access Environment Variables

1. Go to your application in Coolify
2. Click on **"Environment Variables"** or **"Variables"** tab
3. Click **"Add Variable"** or **"New Variable"**

### Step 2: Add Required Variables

Add these **7 required variables** one by one:

#### 1. TELEGRAM_API_ID
- **Name**: `TELEGRAM_API_ID`
- **Value**: Your Telegram API ID (integer, e.g., `12345678`)
- **Example**: `12345678`

#### 2. TELEGRAM_API_HASH
- **Name**: `TELEGRAM_API_HASH`
- **Value**: Your Telegram API hash (string)
- **Example**: `abcdef1234567890abcdef1234567890`

#### 3. TELEGRAM_PHONE
- **Name**: `TELEGRAM_PHONE`
- **Value**: Your phone number with country code
- **Example**: `+1234567890`
- **Important**: Must include `+` and country code

#### 4. TELEGRAM_GROUP
- **Name**: `TELEGRAM_GROUP`
- **Value**: Telegram group username (without @) or invite link
- **Example**: `mygroup` or `https://t.me/mygroup`

#### 5. AIRTABLE_TOKEN
- **Name**: `AIRTABLE_TOKEN`
- **Value**: Your Airtable personal access token
- **Example**: `patxxxxxxxxxxxxx`

#### 6. AIRTABLE_BASE_ID
- **Name**: `AIRTABLE_BASE_ID`
- **Value**: Your Airtable base ID
- **Example**: `appxxxxxxxxxxxxx`

#### 7. AIRTABLE_TABLE
- **Name**: `AIRTABLE_TABLE`
- **Value**: Your Airtable table name
- **Example**: `Courses`

### Step 3: Save and Restart

1. **Save** all environment variables
2. **Restart** the container/application
3. Check **Logs** to verify it's working

## 📋 Quick Copy-Paste Checklist

Use this checklist to ensure all variables are set:

```
☐ TELEGRAM_API_ID
☐ TELEGRAM_API_HASH
☐ TELEGRAM_PHONE
☐ TELEGRAM_GROUP
☐ AIRTABLE_TOKEN
☐ AIRTABLE_BASE_ID
☐ AIRTABLE_TABLE
```

## 🔍 How to Get Your Credentials

### Telegram API Credentials

1. Go to: https://my.telegram.org/apps
2. Login with your phone number
3. Create a new application (if needed)
4. Copy:
   - **api_id**: The number shown (e.g., `12345678`)
   - **api_hash**: The hash string (e.g., `abcdef1234...`)

### Airtable Credentials

1. Go to: https://airtable.com/create/tokens
2. Create a new personal access token
3. Give it these scopes:
   - `data.records:read`
   - `data.records:write`
4. Copy the token
5. Get Base ID from your Airtable base URL:
   - URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
   - Base ID: `appXXXXXXXXXXXXXX`
6. Get table name from your Airtable base

## ✅ Verification

After setting all variables, check the logs. You should see:

```
✓ Airtable connected
✓ Found existing session file, attempting to connect...
✓ Connected using existing session
Scanning messages for studybullet.com URLs...
```

If you still see errors, check:
1. Variable names are **exactly** as shown (case-sensitive)
2. No extra spaces in variable names or values
3. Values don't have quotes (Coolify adds them automatically)
4. Container has been restarted after adding variables

## 🐛 Common Issues

### Variable Not Found
- **Problem**: Variable name has typo
- **Solution**: Check spelling, case sensitivity

### Wrong Type Error
- **Problem**: `TELEGRAM_API_ID` is not a number
- **Solution**: Make sure it's an integer (e.g., `12345678`, not `"12345678"`)

### Still Getting NoneType Error
- **Problem**: Variables not saved or container not restarted
- **Solution**: 
  1. Verify variables are saved in Coolify UI
  2. Restart the container
  3. Check logs again

## 📝 Example Environment Variables (Don't Use These!)

```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+1234567890
TELEGRAM_GROUP=mygroup
AIRTABLE_TOKEN=patxxxxxxxxxxxxx
AIRTABLE_BASE_ID=appxxxxxxxxxxxxx
AIRTABLE_TABLE=Courses
```

**Note**: Replace with your actual values!

---

**After setting variables, restart the container and check logs!**
