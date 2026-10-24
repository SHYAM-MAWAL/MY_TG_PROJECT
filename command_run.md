# How to Run the Telegram Course Scraper

## Quick Start

### Single Run (One-time execution)
```bash
python main.py
```

### Automated Run (Runs every 5 minutes continuously)
```bash
python main.py
```
*Note: The script now runs automatically every 5 minutes. Press `Ctrl+C` to stop.*

---

## Step-by-Step Instructions

### Prerequisites

1. **Python 3.10+ installed**
   - Check version: `python --version`
   - Download from: https://www.python.org/downloads/

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install individually:
   ```bash
   pip install telethon requests lxml python-dotenv pyairtable Pillow
   ```

3. **Configure environment variables**
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

### First-Time Setup

1. **Navigate to project directory**
   ```bash
   cd "C:\Cursor Projects\First Cursor project"
   ```

2. **Authenticate with Telegram (first run only)**
   ```bash
   python auth_telegram.py
   ```
   - Enter the verification code sent to your phone
   - Enter 2FA password if enabled
   - A session file will be created for future runs

### Running the Project

#### Option 1: Automated Continuous Run (Recommended)

**Command:**
```bash
python main.py
```

**What it does:**
- Scans last 15 messages from Telegram group
- Extracts StudyBullet URLs
- Converts to Udemy URLs
- Saves to Airtable with images
- Repeats every 5 minutes automatically
- Press `Ctrl+C` to stop

**Output:**
```
================================================================================
AUTOMATED COURSE SCRAPER - Running every 5 minutes
Press Ctrl+C to stop
================================================================================

================================================================================
RUN #1 - 2026-01-12 10:30:00
================================================================================
...
[Processes courses]
...
Waiting 5 minutes until next run...
```

#### Option 2: Single Run (For Testing)

If you want to run once and exit, you can modify the code or use a timeout:

**Windows PowerShell:**
```powershell
timeout /t 60 python main.py
```

**Or modify main.py temporarily** to remove the continuous loop.

### Running in Background (Windows)

#### Using PowerShell (Background Job)
```powershell
Start-Job -ScriptBlock { cd "C:\Cursor Projects\First Cursor project"; python main.py }
```

#### Using Task Scheduler (Windows)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "When I log on" or "At startup"
4. Action: Start a program
5. Program: `python`
6. Arguments: `"C:\Cursor Projects\First Cursor project\main.py"`
7. Start in: `"C:\Cursor Projects\First Cursor project"`

#### Using Command Prompt (Background)
```cmd
start /B python main.py
```

### Running on Linux/Mac

#### Using nohup (Background)
```bash
nohup python main.py > scraper.log 2>&1 &
```

#### Using screen (Detached session)
```bash
screen -S scraper
python main.py
# Press Ctrl+A then D to detach
# Reattach with: screen -r scraper
```

#### Using systemd (Service)
Create `/etc/systemd/system/telegram-scraper.service`:
```ini
[Unit]
Description=Telegram Course Scraper
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 /path/to/project/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable telegram-scraper
sudo systemctl start telegram-scraper
sudo systemctl status telegram-scraper
```

---

## Commands Reference

### Main Commands

| Command | Description |
|---------|-------------|
| `python main.py` | Run automated scraper (every 5 minutes) |
| `python auth_telegram.py` | Authenticate Telegram (first time only) |
| `python auth_telegram.py --code 12345` | Authenticate with code from command line |

### Verification Commands

```bash
# Check if dependencies are installed
python -c "import telethon, requests, lxml; print('OK')"

# Test Airtable connection
python -c "from airtable_handler import AirtableHandler; AirtableHandler()"

# Check environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API ID:', os.getenv('TELEGRAM_API_ID'))"
```

---

## Troubleshooting

### Issue: "Module not found"
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Authentication required"
**Solution:** Run authentication script
```bash
python auth_telegram.py
```

### Issue: "Airtable connection failed"
**Solution:** Check `.env` file has correct credentials

### Issue: "Webhook errors"
**Solution:** Webhook functionality has been removed. This is normal.

### Issue: Script stops after one run
**Solution:** Make sure you're using the latest version with continuous loop

### Issue: Want to stop the automation
**Solution:** Press `Ctrl+C` in the terminal

---

## Project Structure

```
First Cursor project/
├── main.py                 # Main scraper script (automated)
├── auth_telegram.py        # Telegram authentication helper
├── airtable_handler.py     # Airtable integration
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create from template)
├── env_template.txt        # Environment variables template
├── command_run.md          # This file
└── README.md               # Project documentation
```

---

## Configuration

### Change Fetch Count
Edit `main.py` line 238:
```python
async for message in client.iter_messages(entity, limit=15):  # Change 15 to desired number
```

### Change Interval (5 minutes)
Edit `main.py` line 377:
```python
await asyncio.sleep(300)  # 300 seconds = 5 minutes, change as needed
```

### Disable Automation (Single Run)
Comment out the continuous loop in `main.py`:
```python
# Replace run_continuously() with:
asyncio.run(main())
```

---

## Monitoring

The script outputs:
- Run number and timestamp
- Messages scanned
- URLs found and extracted
- Airtable insertions
- Duplicates skipped
- Errors (if any)

Check the console output for real-time status.

---

## Support

For issues or questions:
1. Check the error messages in console
2. Verify `.env` configuration
3. Ensure all dependencies are installed
4. Check Airtable field types match expected format
