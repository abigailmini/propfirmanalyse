-- PropAnalyse analytics schema v1. No raw IPs, no cookies: "visitor" is
-- sha256(daily random salt | ip | user-agent) truncated to 16 hex chars; the salt is
-- deleted after 48h, so visitors cannot be linked across days or re-identified.

CREATE TABLE IF NOT EXISTS pageviews (
  id INTEGER PRIMARY KEY,
  ts INTEGER NOT NULL,            -- unix ms
  day TEXT NOT NULL,              -- YYYY-MM-DD in TZ_OFFSET_MIN
  path TEXT NOT NULL,
  ref_host TEXT NOT NULL DEFAULT '',
  utm_source TEXT NOT NULL DEFAULT '',
  utm_medium TEXT NOT NULL DEFAULT '',
  utm_campaign TEXT NOT NULL DEFAULT '',
  lang TEXT NOT NULL DEFAULT '',
  device TEXT NOT NULL DEFAULT '',
  country TEXT NOT NULL DEFAULT '',
  visitor TEXT                    -- NULL when DNT/GPC
);
CREATE INDEX IF NOT EXISTS pv_day ON pageviews(day, path);

CREATE TABLE IF NOT EXISTS clicks (
  id INTEGER PRIMARY KEY,
  ts INTEGER NOT NULL,
  day TEXT NOT NULL,
  firm TEXT NOT NULL,
  dest_kind TEXT NOT NULL,        -- affiliate | site | home (unknown slug)
  src TEXT NOT NULL DEFAULT '',   -- page the click came from
  pos TEXT NOT NULL DEFAULT '',   -- slot: table, offer-card, firm-page, compare, list, cta, text
  code TEXT NOT NULL DEFAULT '',  -- promo code shown next to the link
  country TEXT NOT NULL DEFAULT '',
  device TEXT NOT NULL DEFAULT '',
  ref_host TEXT NOT NULL DEFAULT '',
  visitor TEXT
);
CREATE INDEX IF NOT EXISTS ck_day ON clicks(day, firm);

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY,
  ts INTEGER NOT NULL,
  day TEXT NOT NULL,
  kind TEXT NOT NULL,             -- copy (promo code copied) | out (other outbound link)
  firm TEXT NOT NULL DEFAULT '',
  code TEXT NOT NULL DEFAULT '',
  path TEXT NOT NULL DEFAULT '',
  target_host TEXT NOT NULL DEFAULT '',
  country TEXT NOT NULL DEFAULT '',
  device TEXT NOT NULL DEFAULT '',
  visitor TEXT
);
CREATE INDEX IF NOT EXISTS ev_day ON events(day, kind);

CREATE TABLE IF NOT EXISTS submissions (
  id INTEGER PRIMARY KEY,
  ts INTEGER NOT NULL,
  day TEXT NOT NULL,
  kind TEXT NOT NULL,             -- complaint | listing | correction | review | status-review
  firm TEXT NOT NULL DEFAULT '',
  email TEXT NOT NULL DEFAULT '',
  payload TEXT NOT NULL,          -- JSON of the submitted fields
  page TEXT NOT NULL DEFAULT '',
  lang TEXT NOT NULL DEFAULT '',
  country TEXT NOT NULL DEFAULT '',
  visitor TEXT,
  status TEXT NOT NULL DEFAULT 'new',  -- new | reviewing | resolved | rejected | spam
  note TEXT NOT NULL DEFAULT '',
  notified INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS sub_status ON submissions(status, ts);
CREATE INDEX IF NOT EXISTS sub_day ON submissions(day);

CREATE TABLE IF NOT EXISTS bot_hits (
  day TEXT NOT NULL,
  kind TEXT NOT NULL,             -- click | beacon
  reason TEXT NOT NULL,           -- ua | head | noua | nolang | prefetch
  n INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, kind, reason)
);

CREATE TABLE IF NOT EXISTS salts (
  day TEXT PRIMARY KEY,
  salt TEXT NOT NULL
);
