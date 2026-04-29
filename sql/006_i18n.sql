-- User profile locale (D-60 i18n infrastructure). Idempotent.
ALTER TABLE user_profiles
  ADD COLUMN IF NOT EXISTS locale text NOT NULL DEFAULT 'pl'
    CHECK (locale IN ('pl', 'en'));
