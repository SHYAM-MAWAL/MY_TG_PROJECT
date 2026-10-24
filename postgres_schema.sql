-- Run manually if you prefer (handler also auto-creates this table)

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

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
