import os
from contextlib import contextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

TABLE = "courses"


class PostgresHandler:
    def __init__(self):
        self.dsn = self._build_dsn()
        if not self.dsn:
            raise ValueError(
                "Missing Postgres config. Set DATABASE_URL or "
                "POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB"
            )
        import psycopg2  # noqa: F401 — validate install early

        self._ensure_schema()

    def _build_dsn(self):
        url = os.getenv("DATABASE_URL")
        if url:
            return url

        host = os.getenv("POSTGRES_HOST")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        db = os.getenv("POSTGRES_DB", "postgres")
        port = os.getenv("POSTGRES_PORT", "5432")
        sslmode = os.getenv("POSTGRES_SSLMODE", "prefer")

        if not all([host, user, password]):
            return None

        return (
            f"host={host} port={port} dbname={db} "
            f"user={user} password={password} sslmode={sslmode}"
        )

    @contextmanager
    def _conn(self):
        import psycopg2

        conn = psycopg2.connect(self.dsn)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_schema(self):
        with self._conn() as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
                except Exception:
                    pass
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS courses (
                      id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                      course_title TEXT NOT NULL,
                      target_url   TEXT NOT NULL UNIQUE,
                      image        TEXT,
                      status       TEXT NOT NULL DEFAULT 'Pending',
                      created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    CREATE INDEX IF NOT EXISTS idx_courses_status ON courses (status);
                    CREATE INDEX IF NOT EXISTS idx_courses_created ON courses (created_at DESC);
                    """
                )

    def check_if_exists(self, target_url):
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM courses WHERE target_url = %s LIMIT 1",
                        (target_url,),
                    )
                    return cur.fetchone() is not None
        except Exception as e:
            print(f"  ⚠ Postgres check error: {e}")
            return False

    def insert_course(self, title, target_url, image_base64=None, created_at=None):
        try:
            if not image_base64:
                img = None
            elif not image_base64.startswith("data:image"):
                image_base64 = f"data:image/jpeg;base64,{image_base64}"
                img = image_base64 if len(image_base64) <= 100000 else None
            else:
                img = image_base64 if len(image_base64) <= 100000 else None

            if image_base64 and img is None:
                print(f"  ⚠ Image too large ({len(image_base64)} chars), storing without image")

            created = created_at or datetime.now(timezone.utc).isoformat()

            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO courses (course_title, target_url, image, status, created_at)
                        VALUES (%s, %s, %s, 'Pending', %s)
                        ON CONFLICT (target_url) DO NOTHING
                        RETURNING id
                        """,
                        (
                            str(title)[:1000] if title else "No title",
                            str(target_url)[:2000],
                            img,
                            created,
                        ),
                    )
                    row = cur.fetchone()
                    if row:
                        print(f"  ✓ Inserted into Postgres")
                        return True
                    print(f"  ℹ️ Already exists in Postgres, skipped")
                    return False
        except Exception as e:
            print(f"  ✗ Postgres insert error: {e}")
            return False

    def get_all_courses(self, limit=200, include_image=False):
        """List courses newest-first. Images omitted by default for fast frontend loads."""
        try:
            limit = max(1, min(int(limit), 500))
            cols = (
                "id, course_title, target_url, image, status, created_at"
                if include_image
                else "id, course_title, target_url, status, created_at, (image IS NOT NULL AND image <> '') AS has_image"
            )
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        SELECT {cols}
                        FROM courses
                        ORDER BY created_at DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                    names = [d[0] for d in cur.description]
                    return [dict(zip(names, row)) for row in cur.fetchall()]
        except Exception as e:
            print(f"  ✗ Postgres fetch error: {e}")
            return []

    def get_course_image(self, course_id):
        """Return image data-URL for one course, or None."""
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT image FROM courses WHERE id = %s LIMIT 1",
                        (course_id,),
                    )
                    row = cur.fetchone()
                    return row[0] if row else None
        except Exception as e:
            print(f"  ✗ Postgres image fetch error: {e}")
            return None

    def mark_completed(self, record_id):
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE courses SET status = 'Completed' WHERE id = %s",
                        (record_id,),
                    )
            return True
        except Exception as e:
            print(f"  ✗ Postgres update error: {e}")
            return False

    def purge_older_than_days(self, days=3):
        """Delete courses older than `days` (based on created_at). Returns rows deleted."""
        try:
            days = max(1, int(days))
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        DELETE FROM courses
                        WHERE created_at < NOW() - (%s * INTERVAL '1 day')
                        RETURNING id
                        """,
                        (days,),
                    )
                    return len(cur.fetchall())
        except Exception as e:
            print(f"  ✗ Postgres purge error: {e}")
            return 0
