"""
One-time Telegram authentication script.
Run this once to authenticate, then main.py will work automatically.
Usage: python auth_telegram.py [--code CODE] [--password PASSWORD]
"""
import sys
import os
import argparse
from io import BytesIO

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from telethon import TelegramClient
from dotenv import load_dotenv

# Parse command line arguments
parser = argparse.ArgumentParser(description='Telegram Authentication')
parser.add_argument('--code', type=str, help='Telegram verification code')
parser.add_argument('--password', type=str, help='Telegram 2FA password')
args = parser.parse_args()

# Load environment variables
load_dotenv()

# Telegram API credentials from .env
api_id = int(os.getenv('TELEGRAM_API_ID'))
api_hash = os.getenv('TELEGRAM_API_HASH')
phone = os.getenv('TELEGRAM_PHONE')

# Create Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    print("\n" + "="*60)
    print("TELEGRAM AUTHENTICATION")
    print("="*60)
    print(f"Phone: {phone}")
    
    # Code callback
    def code_callback():
        if args.code:
            print(f"\n✓ Using code from command line: {args.code}")
            return args.code
        code = os.getenv('TELEGRAM_CODE')
        if code:
            print(f"\n✓ Using code from environment variable")
            return code
        try:
            return input('\nPlease enter the code you received: ')
        except (EOFError, KeyboardInterrupt):
            print("\n✗ Authentication cancelled.")
            sys.exit(1)
    
    # Password callback for 2FA
    def password_callback():
        if args.password:
            print(f"✓ Using password from command line")
            return args.password
        password = os.getenv('TELEGRAM_PASSWORD')
        if password:
            print(f"✓ Using password from environment variable")
            return password
        try:
            return input('Please enter your 2FA password: ')
        except (EOFError, KeyboardInterrupt):
            print("\n✗ Authentication cancelled.")
            sys.exit(1)
    
    if not args.code and not os.getenv('TELEGRAM_CODE'):
        print("\nTelegram will send a verification code to your phone.")
        print("Enter it when prompted below, or use --code argument.\n")
    
    await client.start(phone=phone, code_callback=code_callback, password=password_callback)
    
    print("\n✓ Authentication successful!")
    print("✓ Session saved. You can now run main.py without authentication.")
    print("="*60 + "\n")
    
    await client.disconnect()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nAuthentication cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Authentication failed: {str(e)}")
        sys.exit(1)
