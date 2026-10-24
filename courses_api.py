"""
Public courses API for https://courses.shyamai.in/

  GET /courses                 — fast list (no base64 images by default)
  GET /courses?include_image=1 — full payload (slow; avoid in UI)
  GET /courses/{id}/image      — single course image (lazy-loaded by cards)
  GET /health

Run:  python courses_api.py
"""
import base64
import json
import os
import re
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from postgres_handler import PostgresHandler

pg = PostgresHandler()
PORT = int(os.getenv("PORT", "8080"))
try:
    COURSE_PURGE_DAYS = max(1, int(os.getenv("COURSE_PURGE_DAYS", "3")))
except ValueError:
    COURSE_PURGE_DAYS = 3

# Short in-memory cache so refresh feels instant
_LIST_CACHE = {"key": None, "at": 0.0, "body": b""}
_LIST_TTL_SEC = 15
_LAST_PURGE_AT = 0.0
_PURGE_EVERY_SEC = 3600  # also purge from API hourly if scraper is down

UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[api] {self.address_string()} {fmt % args}")

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "public, max-age=15")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/health":
            return self._send_json(200, {"ok": True})

        # GET /courses/{id}/image
        m = re.match(r"^/courses/([^/]+)/image$", path)
        if m:
            return self._serve_image(m.group(1))

        if path == "/courses":
            return self._serve_list(parse_qs(parsed.query))

        return self._send_json(404, {"error": "not found"})

    def _maybe_purge(self):
        global _LAST_PURGE_AT, _LIST_CACHE
        now = time.time()
        if now - _LAST_PURGE_AT < _PURGE_EVERY_SEC:
            return
        _LAST_PURGE_AT = now
        try:
            deleted = pg.purge_older_than_days(COURSE_PURGE_DAYS)
            if deleted:
                _LIST_CACHE = {"key": None, "at": 0.0, "body": b""}
                print(f"[api] purged {deleted} course(s) older than {COURSE_PURGE_DAYS} day(s)")
        except Exception as e:
            print(f"[api] purge error: {e}")

    def _serve_list(self, qs):
        self._maybe_purge()
        try:
            limit = min(int(qs.get("limit", ["200"])[0]), 500)
        except ValueError:
            limit = 200
        include_image = qs.get("include_image", ["0"])[0] in ("1", "true", "yes")

        cache_key = f"{limit}:{int(include_image)}"
        now = time.time()
        if (
            not include_image
            and _LIST_CACHE["key"] == cache_key
            and now - _LIST_CACHE["at"] < _LIST_TTL_SEC
        ):
            return self._send_bytes(200, _LIST_CACHE["body"], "application/json; charset=utf-8")

        rows = pg.get_all_courses(limit=limit, include_image=include_image)
        out = []
        for r in rows:
            item = {
                "id": str(r.get("id")),
                "course_title": r.get("course_title"),
                "target_url": r.get("target_url"),
                "status": r.get("status") or "Pending",
                "created_at": _json_default(r.get("created_at")),
                "has_image": bool(r.get("has_image")) if "has_image" in r else bool(r.get("image")),
            }
            if include_image:
                item["image"] = r.get("image")
            else:
                item["image"] = None
            out.append(item)

        body = json.dumps(out, default=_json_default).encode("utf-8")
        if not include_image:
            _LIST_CACHE["key"] = cache_key
            _LIST_CACHE["at"] = now
            _LIST_CACHE["body"] = body
        return self._send_bytes(200, body, "application/json; charset=utf-8")

    def _serve_image(self, course_id):
        if not UUID_RE.match(course_id):
            return self._send_json(400, {"error": "invalid id"})

        image = pg.get_course_image(course_id)
        if not image:
            return self._send_json(404, {"error": "no image"})

        # Prefer raw jpeg/png bytes so <img src> is fast
        mime = "image/jpeg"
        raw = None
        if isinstance(image, str) and image.startswith("data:image"):
            try:
                header, b64 = image.split(",", 1)
                if "png" in header:
                    mime = "image/png"
                elif "webp" in header:
                    mime = "image/webp"
                raw = base64.b64decode(b64)
            except Exception:
                raw = None

        if raw:
            # Cache thumbnails a bit longer in the browser
            self.send_response(200)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "public, max-age=3600")
            self.end_headers()
            self.wfile.write(raw)
            return

        return self._send_json(200, {"image": image})

    def _send_json(self, code, payload):
        body = json.dumps(payload, default=_json_default).encode("utf-8")
        return self._send_bytes(code, body, "application/json; charset=utf-8")

    def _send_bytes(self, code, body: bytes, content_type: str):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Courses API on http://0.0.0.0:{PORT}  (GET /courses — images lazy)")
    server.serve_forever()
