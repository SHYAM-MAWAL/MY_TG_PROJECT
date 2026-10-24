"""
Authenticate via QR code (no SMS / login-code message needed).

QR tokens expire in ~30–60 seconds. Scan immediately when a new QR appears.

1. Run: python auth_telegram_qr.py
2. Phone: Telegram → Settings → Devices → Link Desktop Device
3. Scan telegram_qr.png (Preview opens automatically) RIGHT AWAY
"""
import asyncio
import os
import subprocess
import sys

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
session_path = os.getenv("SESSION_PATH") or "session_name"
QR_PNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telegram_qr.png")


def show_qr(url: str, attempt: int) -> None:
    import qrcode

    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    qrcode.make(url).save(QR_PNG)

    # Re-open Preview so you always see the FRESH token
    try:
        subprocess.run(["open", "-a", "Preview", QR_PNG], check=False)
    except Exception:
        pass

    print("\n" + "!" * 60)
    print(f"  SCAN THIS QR NOW  (attempt {attempt}) — expires in ~30s")
    print(f"  File: {QR_PNG}")
    print("  Phone: Settings → Devices → Link Desktop Device")
    print("!" * 60 + "\n")


async def main() -> None:
    print("\n" + "=" * 60)
    print("TELEGRAM QR LOGIN (fast refresh)")
    print("=" * 60)

    client = TelegramClient(session_path, api_id, api_hash)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"Already logged in as: {me.first_name} (@{me.username}) id={me.id}")
        await client.disconnect()
        return

    qr = await client.qr_login()
    show_qr(qr.url, 1)

    # Short timeout so PNG never stays stale for long
    for attempt in range(1, 13):
        try:
            await qr.wait(timeout=25)
            break
        except asyncio.TimeoutError:
            print("Token expired (no scan) — new QR incoming...\n")
            await qr.recreate()
            show_qr(qr.url, attempt + 1)
        except SessionPasswordNeededError:
            password = os.getenv("TELEGRAM_PASSWORD")
            if not password:
                try:
                    password = input("2FA enabled. Enter your Telegram cloud password: ")
                except (EOFError, KeyboardInterrupt):
                    print("\nCancelled.")
                    await client.disconnect()
                    sys.exit(1)
            await client.sign_in(password=password)
            break
    else:
        print("\n✗ Timed out. Run again and scan within ~20 seconds of the new QR.")
        await client.disconnect()
        sys.exit(1)

    if not await client.is_user_authorized():
        try:
            await client.get_me()
        except Exception:
            password = os.getenv("TELEGRAM_PASSWORD") or input(
                "2FA enabled. Enter your Telegram cloud password: "
            )
            await client.sign_in(password=password)

    me = await client.get_me()
    print("\n✓ Authentication successful!")
    print(f"✓ Logged in as: {me.first_name} (@{me.username}) id={me.id}")
    print(f"✓ Session saved: {session_path}.session")
    print("You can now run: python main.py")
    print("=" * 60 + "\n")
    await client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ QR login failed: {type(e).__name__}: {e}")
        sys.exit(1)
