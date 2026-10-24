import sys
import os
import argparse
from io import BytesIO

# Fix Unicode encoding for Windows console (skip in Docker/Linux)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        pass  # Skip if not available (e.g., in Docker)

from telethon import TelegramClient
from telethon.errors import (
    AuthKeyDuplicatedError,
    AuthKeyUnregisteredError,
    SessionRevokedError,
)
import re
import requests
from lxml import html
import time
import base64
import glob
import shutil
from datetime import datetime
from dotenv import load_dotenv
from postgres_handler import PostgresHandler

# Parse command line arguments
parser = argparse.ArgumentParser(description='Telegram Course Scraper')
parser.add_argument('--code', type=str, help='Telegram verification code')
parser.add_argument('--password', type=str, help='Telegram 2FA password')
args = parser.parse_args()

# Load environment variables
load_dotenv()

# Telegram API credentials from .env with validation
def get_env_var(name, required=True, var_type=str):
    """Get environment variable with validation"""
    value = os.getenv(name)
    if value is None:
        if required:
            print(f"\n✗ ERROR: Required environment variable '{name}' is not set!")
            print(f"   Please set this variable in Coolify's environment settings.")
            print(f"   Required variables: TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE, TELEGRAM_GROUP")
            sys.exit(1)
        return None
    
    if var_type == int:
        try:
            return int(value)
        except ValueError:
            print(f"\n✗ ERROR: Environment variable '{name}' must be an integer, got: {value}")
            sys.exit(1)
    
    return value

api_id = get_env_var('TELEGRAM_API_ID', required=True, var_type=int)
api_hash = get_env_var('TELEGRAM_API_HASH', required=True)
phone = get_env_var('TELEGRAM_PHONE', required=True)
target_group = get_env_var('TELEGRAM_GROUP', required=True)

# Initialize Postgres handler (only storage backend)
db = None
try:
    db = PostgresHandler()
    print(f"✓ Postgres connected")
except Exception as e:
    print(f"⚠ Postgres not configured: {str(e)}")

# Auto-purge courses older than N days (default 3)
try:
    COURSE_PURGE_DAYS = int(os.getenv("COURSE_PURGE_DAYS", "3"))
except ValueError:
    COURSE_PURGE_DAYS = 3
COURSE_PURGE_DAYS = max(1, COURSE_PURGE_DAYS)

# In-memory set for fast duplicate tracking during execution
processed_urls = set()

# Persistent cache of StudyBullet URLs we've already visited — avoids slow re-visits
SEEN_SOURCE_URLS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seen_source_urls.txt')
seen_source_urls: set = set()

def load_seen_source_urls():
    global seen_source_urls
    try:
        if os.path.exists(SEEN_SOURCE_URLS_FILE):
            with open(SEEN_SOURCE_URLS_FILE) as f:
                seen_source_urls = set(line.strip() for line in f if line.strip())
            print(f"✓ Loaded {len(seen_source_urls)} cached StudyBullet URLs")
    except Exception:
        seen_source_urls = set()

def save_seen_source_url(url):
    seen_source_urls.add(url)
    try:
        with open(SEEN_SOURCE_URLS_FILE, 'a') as f:
            f.write(url + '\n')
    except Exception:
        pass

load_seen_source_urls()

# Regex to match URLs starting with https://studybullet.com/course
url_regex = re.compile(r'https://studybullet\.com/course[^\s)\]>\"\']*')

# XPath patterns to extract Udemy URLs
xpath_patterns = [
    '//div[contains(@class, "entry-content")]//a[contains(@href, "udemy.com")]/@href',
    '//div[contains(@class, "entry-content")]//a[contains(text(), "Download")]/@href',
    '//a[contains(@class, "maxbutton")]/@href',
    '//article//a[contains(@href, "udemy.com")]/@href',
    '//div[@class="entry-content"]//p//a/@href',
]

# Determine session path (Docker vs local)
session_path = os.getenv('SESSION_PATH')
if not session_path:
    if os.path.exists('/app'):
        # Running in Docker/Coolify
        session_dir = '/app/sessions'
        os.makedirs(session_dir, exist_ok=True)
        session_path = os.path.join(session_dir, 'session_name')
    else:
        # Running locally
        session_path = 'session_name'

# Create Telegram client
client = TelegramClient(session_path, api_id, api_hash)

# Lock file while auth_telegram_qr.py is running (same volume as the session)
AUTH_LOCK_STALE_SECONDS = 10 * 60  # 10 minutes


def auth_lock_path():
    session_dir = os.path.dirname(session_path) or "."
    return os.path.join(session_dir, ".auth_in_progress")


def is_auth_lock_active():
    """True if QR/auth is in progress. Stale locks (>10 min) are ignored."""
    path = auth_lock_path()
    if not os.path.exists(path):
        return False
    try:
        age = time.time() - os.path.getmtime(path)
    except OSError:
        return False
    if age > AUTH_LOCK_STALE_SECONDS:
        print(
            f"⚠ Auth lock is stale ({int(age)}s old, limit {AUTH_LOCK_STALE_SECONDS}s) "
            f"— ignoring {path}"
        )
        return False
    return True


def is_sqlite_locked_error(exc):
    msg = str(exc).lower()
    return "database is locked" in msg or (
        "operationalerror" in msg and "locked" in msg
    )


def is_session_revoked_error(exc):
    return isinstance(
        exc,
        (AuthKeyUnregisteredError, SessionRevokedError, AuthKeyDuplicatedError),
    ) or any(
        name in type(exc).__name__
        for name in (
            "AuthKeyUnregisteredError",
            "SessionRevokedError",
            "AuthKeyDuplicatedError",
        )
    )


def backup_revoked_session_files(path):
    """Rename session files to .bak-<timestamp> instead of deleting them."""
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    session_dir = os.path.dirname(path) or "."
    session_base = os.path.basename(path)
    pattern = os.path.join(session_dir, f"{session_base}.session*")
    moved = []
    for file_path in glob.glob(pattern):
        # Keep existing backups
        if ".bak-" in os.path.basename(file_path):
            continue
        dest = f"{file_path}.bak-{ts}"
        try:
            shutil.move(file_path, dest)
            moved.append(dest)
        except Exception as e:
            print(f"⚠ Could not backup {file_path}: {e}")
    return moved


def check_if_processed(target_url):
    """Check if URL was already processed in this run (in-memory, fast)"""
    if target_url in processed_urls:
        print(f"  ℹ️ URL already processed in this run")
        return True
    processed_urls.add(target_url)
    return False


async def download_image_as_base64(client, message):
    """Download image from Telegram message and convert to base64 (simple conversion)"""
    try:
        if not message.photo:
            return None
        
        # Download the photo to memory
        buffer = BytesIO()
        photo_bytes = await client.download_media(message.photo, file=buffer)
        
        # download_media returns the file object when file parameter is provided
        if photo_bytes:
            photo_bytes.seek(0)
            image_data = photo_bytes.read()
            if image_data:
                # Convert to base64 (simple conversion without compression)
                base64_image = base64.b64encode(image_data).decode('utf-8')
                data_url = f"data:image/jpeg;base64,{base64_image}"
                print(f"  ✓ Image downloaded and converted to base64 ({len(base64_image)} chars)")
                return data_url
        
        return None
        
    except Exception as e:
        print(f"  ✗ Error downloading image: {str(e)}")
        return None


def extract_title_from_message(message_text):
    """Extract the title/first line from Telegram message"""
    if not message_text:
        return "No title"
    
    # Split by newlines and get first non-empty line
    lines = message_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        # Skip emoji-only lines or very short lines
        if len(line) > 10 and not line.startswith('🔗') and not line.startswith('Enroll'):
            # Clean up the title - remove || and extra spaces
            title = line.replace('||', '').strip()
            # Remove excessive spaces
            title = ' '.join(title.split())
            return title
    
    return lines[0][:100] if lines else "No title"


def extract_url_from_xpath(page_url):
    """Visit a URL and extract href using multiple XPath patterns"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(page_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        tree = html.fromstring(response.content)
        
        # Try each XPath pattern until we find a match
        for xpath in xpath_patterns:
            try:
                results = tree.xpath(xpath)
                if results:
                    # Filter out invalid URLs and return the first valid one
                    for result in results:
                        url = str(result).strip()
                        if url and url.startswith('http'):
                            print(f"  ✓ Found Udemy URL")
                            return url
            except Exception:
                continue
        
        print(f"  ✗ No Udemy URL found")
        return None
        
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout after 15 seconds")
        return None
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return None


async def _disconnect_quietly():
    try:
        await client.disconnect()
    except Exception:
        pass


async def _env_code_login():
    """Authenticate with TELEGRAM_CODE / TELEGRAM_PASSWORD (or CLI args). Never deletes sessions."""
    code_used = False

    def code_callback():
        nonlocal code_used
        if args.code:
            if code_used:
                print("⚠ Code already used. Requesting new code from Telegram...")
                print("   Please check your Telegram app for a new code and update TELEGRAM_CODE")
                raise Exception("Code already used, need new code")
            code_used = True
            print("✓ Using code from command line argument")
            return args.code

        code = os.getenv("TELEGRAM_CODE")
        if code:
            if code_used:
                print("⚠ Code already used. Requesting new code from Telegram...")
                print("   Please check your Telegram app for a new code and update TELEGRAM_CODE")
                raise Exception("Code already used, need new code")
            code_used = True
            print("✓ Using code from environment variable")
            return code

        try:
            return input("Please enter the code you received: ")
        except (EOFError, KeyboardInterrupt):
            print("\n✗ Authentication cancelled. Cannot proceed without code.")
            print("   Tip: Set TELEGRAM_CODE environment variable in Coolify")
            raise

    def password_callback():
        if args.password:
            print("✓ Using password from command line argument")
            return args.password
        password = os.getenv("TELEGRAM_PASSWORD")
        if password:
            print("✓ Using password from environment variable")
            return password
        try:
            return input("Please enter your 2FA password: ")
        except (EOFError, KeyboardInterrupt):
            print("\n✗ Authentication cancelled. Cannot proceed without password.")
            print(
                "   Tip: Use --password argument, set TELEGRAM_PASSWORD environment "
                "variable, or run in interactive terminal"
            )
            sys.exit(1)

    print("🔐 Starting authentication (TELEGRAM_CODE / password)...")
    try:
        await client.start(
            phone=phone, code_callback=code_callback, password=password_callback
        )
        print("✓ Authentication successful!")
        print("✓ Session saved. You can now run without authentication.")
        print("💡 Tip: You can remove TELEGRAM_CODE from environment variables now.")
        return None
    except Exception as e:
        error_msg = str(e)
        print(f"\n✗ Authentication failed: {error_msg}")
        await _disconnect_quietly()

        if is_sqlite_locked_error(e):
            print("⚠ Session database is locked (another process may be using it).")
            print("⚠ Skipping this run — session files left untouched.")
            return None

        if "wait of" in error_msg.lower() and "seconds" in error_msg.lower():
            wait_match = re.search(r"wait of (\d+) seconds", error_msg.lower())
            if wait_match:
                wait_seconds = int(wait_match.group(1))
                wait_minutes = wait_seconds // 60
                print("\n" + "=" * 80)
                print("⚠ RATE LIMITED - Telegram requires waiting")
                print("=" * 80)
                print(
                    f"Telegram requires waiting {wait_minutes} minutes "
                    f"({wait_seconds} seconds) before retry."
                )
                print("\nThe script will retry in 3 minutes (faster than required wait).")
                print("Please ensure TELEGRAM_CODE is updated with a fresh code.")
                print("=" * 80)
                return "RATE_LIMITED"
            print("\n⚠ Rate limited by Telegram. Will retry in 3 minutes...")
            return "RATE_LIMITED"

        if (
            "3 consecutive" in error_msg
            or "rate limit" in error_msg.lower()
            or "too many" in error_msg.lower()
        ):
            print("\n" + "=" * 80)
            print("⚠ RATE LIMITED - Too many failed authentication attempts")
            print("=" * 80)
            print("Telegram has temporarily blocked authentication attempts.")
            print("\nTo fix this:")
            print("1. Wait 10-15 minutes for the rate limit to reset")
            print("2. Request a NEW code from Telegram (old codes expire quickly)")
            print("3. Update TELEGRAM_CODE in Coolify with the fresh code")
            print("4. The script will retry in 3 minutes (faster retry for authentication)")
            print("=" * 80)
            return "RATE_LIMITED"

        if (
            "code" in error_msg.lower()
            or "invalid" in error_msg.lower()
            or "PHONE_CODE" in error_msg
            or "Code already used" in error_msg
        ):
            print("\n⚠ Invalid or expired code.")
            print("   Telegram codes expire quickly (usually within 3-5 minutes).")
            print("   Please request a NEW code from Telegram and update TELEGRAM_CODE variable.")
            print("   Will retry in 3 minutes (faster retry for authentication)...")
            return "AUTH_FAILED"

        print("   Please check your credentials and try again.")
        print("   Will retry in 3 minutes (faster retry for authentication)...")
        return "AUTH_FAILED"


async def main():
    """Main function to scrape Telegram group for course URLs"""
    global client  # Declare global at the start of the function

    if is_auth_lock_active():
        print("\n" + "=" * 80)
        print("⚠ AUTH IN PROGRESS — skipping this run")
        print("=" * 80)
        print(f"Lock file present: {auth_lock_path()}")
        print("Another process (auth_telegram_qr.py) is logging in.")
        print("Session files will NOT be touched.")
        print("=" * 80 + "\n")
        return None

    session_file = f"{session_path}.session"
    if os.path.exists(session_file):
        print("✓ Found existing session file, attempting to connect...")
    else:
        print("⚠ No session file found. First-time authentication required.")

    authorized = False
    try:
        await client.connect()
        try:
            authorized = await client.is_user_authorized()
        except (AuthKeyUnregisteredError, SessionRevokedError, AuthKeyDuplicatedError) as e:
            print(f"⚠ Telegram reports session revoked: {type(e).__name__}")
            await _disconnect_quietly()
            moved = backup_revoked_session_files(session_path)
            if moved:
                print(
                    "✓ Backed up revoked session file(s): "
                    + ", ".join(os.path.basename(f) for f in moved)
                )
            client = TelegramClient(session_path, api_id, api_hash)
            await client.connect()
            authorized = False
    except Exception as e:
        if is_sqlite_locked_error(e):
            print("⚠ Session database is locked (another process may be using it).")
            print("⚠ Skipping this run — session files left untouched.")
            await _disconnect_quietly()
            return None
        if is_session_revoked_error(e):
            print(f"⚠ Telegram reports session revoked: {type(e).__name__}")
            await _disconnect_quietly()
            moved = backup_revoked_session_files(session_path)
            if moved:
                print(
                    "✓ Backed up revoked session file(s): "
                    + ", ".join(os.path.basename(f) for f in moved)
                )
            client = TelegramClient(session_path, api_id, api_hash)
            try:
                await client.connect()
            except Exception as e2:
                if is_sqlite_locked_error(e2):
                    print("⚠ Session database is locked after backup — skipping this run.")
                    return None
                raise
            authorized = False
        else:
            raise

    if authorized:
        print("✓ Connected using existing session")
    else:
        print("⚠ Session not authorized.")
        has_code = args.code or os.getenv("TELEGRAM_CODE")
        if not has_code:
            print("\n" + "=" * 80)
            print("⚠ AUTHENTICATION REQUIRED – run auth_telegram_qr.py")
            print("=" * 80)
            print("Telegram session is missing or not logged in.")
            print("Session files were NOT deleted.")
            print("\nOn Coolify:")
            print("  docker exec -it <telegram-scraper-container> python auth_telegram_qr.py")
            print("  then restart the scraper service.")
            print("\nOr set TELEGRAM_CODE (+ optional TELEGRAM_PASSWORD) and restart.")
            print("=" * 80 + "\n")
            print("⚠ Skipping this run. Will retry later...")
            await _disconnect_quietly()
            return None

        result = await _env_code_login()
        if result is not None:
            return result
        if not await client.is_user_authorized():
            print("⚠ Still not authorized after login attempt — skipping this run.")
            await _disconnect_quietly()
            return None

    print(f"\n{'='*80}")
    print(f"TELEGRAM COURSE SCRAPER")
    print(f"{'='*80}")
    print(f"Target Group: {target_group}")
    print(f"{'='*80}\n")

    # Auto-purge expired courses before each scrape cycle
    if db:
        try:
            purged = db.purge_older_than_days(COURSE_PURGE_DAYS)
            if purged:
                print(f"✓ Purged {purged} course(s) older than {COURSE_PURGE_DAYS} day(s)\n")
            else:
                print(f"✓ Purge check OK — nothing older than {COURSE_PURGE_DAYS} day(s)\n")
        except Exception as e:
            print(f"⚠ Purge failed: {e}\n")
    
    entity = await client.get_entity(target_group)
    print(f"✓ Connected to: {entity.title}\n")
    
    found_data = []
    message_count = 0

    # Load last processed message ID to fetch only new messages
    last_id_file = os.path.join(os.path.dirname(session_path) or '.', 'last_message_id.txt')
    min_id = 0
    try:
        if os.path.exists(last_id_file):
            with open(last_id_file) as f:
                min_id = int(f.read().strip())
            print(f"✓ Fetching messages after ID {min_id}\n")
        else:
            print(f"ℹ️ No last message ID found — fetching last 50 messages\n")
    except Exception:
        min_id = 0

    max_seen_id = min_id

    # Fetch only new messages since last run (or last 50 on first run)
    fetch_limit = None if min_id > 0 else 50
    print(f"Scanning messages for studybullet.com URLs...\n")
    async for message in client.iter_messages(entity, limit=fetch_limit, min_id=min_id):
        message_count += 1
        if message.id > max_seen_id:
            max_seen_id = message.id
        
        # Skip messages without text
        if not message.text:
            continue
        
        # Find studybullet URLs in message
        matches = url_regex.findall(message.text)
        if matches:
            print(f"[Message {message.id}]")
            
            # Extract title from message
            title = extract_title_from_message(message.text)
            print(f"  Title: {title[:80]}...")
            
            # Download image if present and convert to base64
            image_base64 = None
            if message.photo:
                print(f"  📷 Downloading image...")
                image_base64 = await download_image_as_base64(client, message)
            else:
                print(f"  ℹ️ No image")
            
            # Process each URL found in the message
            for url in matches:
                if not any(item['url'] == url for item in found_data):
                    found_data.append({
                        'url': url,
                        'title': title,
                        'message_id': message.id,
                        'image_base64': image_base64,
                        'message_date': message.date.isoformat(),  # Telegram timestamp
                    })
                    print(f"  ✓ URL: {url}")
            print()

    # Save the highest message ID seen so next run only fetches newer messages
    if max_seen_id > min_id:
        try:
            with open(last_id_file, 'w') as f:
                f.write(str(max_seen_id))
            print(f"✓ Saved last message ID: {max_seen_id}")
        except Exception as e:
            print(f"⚠ Could not save last message ID: {e}")

    print(f"{'='*80}")
    print(f"SCAN COMPLETE")
    print(f"{'='*80}")
    print(f"Messages scanned: {message_count}")
    print(f"StudyBullet URLs found: {len(found_data)}")
    print(f"{'='*80}\n")

    # Reverse so oldest Telegram message is processed first → newest gets latest created_at
    found_data.reverse()

    # Extract Udemy URLs
    print(f"{'='*80}")
    print(f"EXTRACTING UDEMY URLS")
    print(f"{'='*80}\n")
    
    successful = 0
    postgres_saved = 0
    duplicates = 0
    
    for i, item in enumerate(found_data, 1):
        try:
            source_url = item['url']
            print(f"[{i}/{len(found_data)}] {source_url}")
            print(f"  Title: {item['title'][:60]}...")

            # Skip StudyBullet HTTP request if we've processed this URL before
            if source_url in seen_source_urls:
                print(f"  ⚡ Already processed (cached), skipping")
                duplicates += 1
                continue

            # Extract Udemy URL with error handling
            try:
                extracted_url = extract_url_from_xpath(source_url)
            except Exception as e:
                print(f"  ✗ Error extracting URL: {str(e)}")
                extracted_url = None
            
            if extracted_url:
                # Fast in-memory duplicate check (prevents processing same URL twice in this run)
                if check_if_processed(extracted_url):
                    duplicates += 1
                    continue
                
                successful += 1
                print(f"  ✓ Udemy URL: {extracted_url}")
                
                if db:
                    try:
                        if db.check_if_exists(extracted_url):
                            print(f"  ℹ️ Already exists in Postgres, skipping")
                            save_seen_source_url(source_url)
                            duplicates += 1
                        else:
                            if db.insert_course(item['title'], extracted_url, item.get('image_base64'), item.get('message_date')):
                                postgres_saved += 1
                                save_seen_source_url(source_url)
                    except Exception as e:
                        print(f"  ⚠ Postgres operation failed: {str(e)}")
                
            else:
                print(f"  ℹ️ No Udemy URL extracted, skipping...")
        
        except Exception as e:
            print(f"  ✗ Unexpected error processing item: {str(e)}")
            print(f"  ⚠ Continuing with next item...")
        
        try:
            time.sleep(1)
        except:
            pass
        print()
    
    print(f"{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Successfully extracted: {successful}/{len(found_data)} URLs")
    print(f"✓ Saved to Postgres: {postgres_saved}")
    print(f"✓ Duplicates skipped: {duplicates}")
    print(f"{'='*80}\n")
    
    # Return None for successful runs (normal 5-minute interval)
    return None


async def run_continuously():
    """Run the scraper continuously every 5 minutes"""
    import asyncio
    from datetime import datetime
    
    print(f"\n{'='*80}")
    print(f"AUTOMATED COURSE SCRAPER - Running every 1 minute")
    print(f"Press Ctrl+C to stop")
    print(f"{'='*80}\n")
    
    run_count = 0
    
    while True:
        try:
            run_count += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'='*80}")
            print(f"RUN #{run_count} - {current_time}")
            print(f"{'='*80}\n")
            
            # Run the main scraping function
            await main()
            
            # Wait 5 minutes (300 seconds) before next run
            print(f"\n{'='*80}")
            print(f"Waiting 5 minutes until next run...")
            print(f"Press Ctrl+C to stop the automation")
            print(f"{'='*80}\n")
            
            await asyncio.sleep(60)  # 1 minute
            
        except KeyboardInterrupt:
            print(f"\n\n{'='*80}")
            print(f"⚠ Automation stopped by user")
            print(f"Total runs completed: {run_count}")
            print(f"{'='*80}\n")
            break
        except Exception as e:
            print(f"\n⚠ Error in run #{run_count}: {str(e)}")
            print(f"Continuing to next run in 5 minutes...\n")
            import traceback
            traceback.print_exc()
            # Wait 5 minutes even after error
            try:
                await asyncio.sleep(60)
            except KeyboardInterrupt:
                print(f"\n\n⚠ Automation stopped by user")
                break


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(run_continuously())
    except KeyboardInterrupt:
        print("\n\n⚠ Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
