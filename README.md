# SHYAMAI Udemy Course Scraper

Automated Telegram course scraper that monitors a Telegram group/channel for StudyBullet course URLs, extracts Udemy URLs, and saves them to Airtable.

## 🚀 Features

- ✅ Automatically fetches last 15 messages from Telegram group/channel
- ✅ Extracts StudyBullet course URLs using regex pattern matching
- ✅ Visits pages and extracts Udemy URLs using multiple XPath patterns
- ✅ Prevents duplicates using in-memory tracking + Airtable persistent storage
- ✅ Downloads and converts images to base64 data URLs
- ✅ Saves to Airtable with default "Pending" status
- ✅ Runs continuously every 5 minutes automatically
- ✅ Production-ready with Docker support for Coolify deployment
- ✅ Comprehensive error handling and logging
- ✅ Cross-platform (Windows, Linux, Docker)

## 📋 Requirements

- Python 3.10+
- Telegram API credentials (from https://my.telegram.org/apps)
- Airtable account with API access
- Telegram group/channel access

## 🛠️ Installation

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy.git
   cd SHYAMAI_Udemy
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   - Copy `env_template.txt` to `.env`
   - Fill in your credentials:
     ```
     TELEGRAM_API_ID=your_api_id
     TELEGRAM_API_HASH=your_api_hash
     TELEGRAM_PHONE=+1234567890
     TELEGRAM_GROUP=your_group_username
     AIRTABLE_TOKEN=your_token
     AIRTABLE_BASE_ID=your_base_id
     AIRTABLE_TABLE=your_table_name
     ```

4. **First-time authentication:**
   ```bash
   python auth_telegram.py
   ```
   Enter the verification code sent to your Telegram.

5. **Run the scraper:**
   ```bash
   python main.py
   ```

### Coolify Deployment

See [QUICK_START_COOLIFY.md](QUICK_START_COOLIFY.md) for step-by-step deployment guide.

**Quick Steps:**
1. Push code to GitHub
2. Create new application in Coolify
3. Connect GitHub repository: `https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy.git`
4. Set environment variables
5. Configure persistent volume for `/app/sessions`
6. Deploy and authenticate

## ⚙️ Configuration

### Environment Variables

**Required:**
- `TELEGRAM_API_ID` - Telegram API ID (integer)
- `TELEGRAM_API_HASH` - Telegram API hash
- `TELEGRAM_PHONE` - Phone number with country code (e.g., +1234567890)
- `TELEGRAM_GROUP` - Group username (without @) or invite link
- `AIRTABLE_TOKEN` - Airtable personal access token
- `AIRTABLE_BASE_ID` - Airtable base ID
- `AIRTABLE_TABLE` - Airtable table name

**Optional:**
- `SESSION_PATH` - Custom session file path (default: auto-detected)
- `TELEGRAM_CODE` - Verification code (first run only)
- `TELEGRAM_PASSWORD` - 2FA password (if enabled)

### Airtable Table Structure

Your Airtable table should have these fields:
- `course_title` (Single line text)
- `target_url` (URL)
- `image` (Long text - stores base64 data URL)
- `created_at` (Date)
- `Status` (Single select: "Pending", "Processing", "Completed", etc.)

### Adjusting Settings

**Change fetch count** (default: 15 messages):
Edit `main.py` line ~238:
```python
async for message in client.iter_messages(entity, limit=15):
```

**Change interval** (default: 5 minutes):
Edit `main.py` line ~379:
```python
await asyncio.sleep(300)  # 300 seconds = 5 minutes
```

## 📊 How It Works

1. **Telegram Scanning**: Fetches last 15 messages from target group
2. **URL Extraction**: Finds StudyBullet URLs matching `https://studybullet.com/course...`
3. **Title Extraction**: Extracts course title from message
4. **Image Download**: Downloads images and converts to base64 data URLs
5. **Udemy URL Extraction**: Visits StudyBullet page and extracts Udemy URL using XPath patterns
6. **Duplicate Check**: 
   - Fast in-memory check (prevents processing same URL twice in one run)
   - Persistent Airtable check (prevents duplicates across runs)
7. **Save to Airtable**: Inserts new courses with default "Pending" status

## 📁 Project Structure

```
SHYAMAI_Udemy/
├── main.py                 # Main scraper script
├── airtable_handler.py     # Airtable integration
├── auth_telegram.py        # One-time Telegram authentication
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── .dockerignore           # Docker build exclusions
├── coolify.yaml            # Coolify deployment config
├── env_template.txt        # Environment variables template
├── README.md               # This file
├── DEPLOYMENT.md           # Detailed deployment guide
├── QUICK_START_COOLIFY.md  # Quick Coolify deployment
└── PRODUCTION_CHECKLIST.md # Production readiness checklist
```

## 🔒 Security

- **Never commit `.env` files** - They contain sensitive credentials
- Session files (`.session`) are excluded from Git
- All secrets should be set via environment variables
- Use Coolify's secret management for production

## 🐛 Troubleshooting

### Authentication Issues
- Delete `session_name.session` and re-authenticate
- Ensure phone number includes country code
- Check internet connection

### No Courses Found
- Verify `TELEGRAM_GROUP` is correct
- Check bot has access to the group
- Ensure messages contain StudyBullet URLs

### Airtable Errors
- Verify credentials are correct
- Check table field names match expected format
- Verify API rate limits

### Container Issues (Coolify)
- Check environment variables are set
- Verify volume mount for `/app/sessions`
- Review container logs for errors

## 📝 License

This project is provided as-is for automation purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs for error messages
3. Verify environment configuration
4. Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides

---

**Repository**: https://github.com/SHYAM-MAWAL/SHYAMAI_Udemy.git
