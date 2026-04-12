-- ═══════════════════════════════════════════════════════════════════════════════
-- Gas Safe App — Supabase Schema
-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor → New Query)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ── Enable UUID generation ─────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════════════════════════════════
-- 1. PROFILES — engineer company & personal data
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS profiles (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username      TEXT NOT NULL,
  display_name  TEXT,
  company_name  TEXT,
  company_type  TEXT,
  company_number TEXT,
  vat_reg_number TEXT,
  company_addr  TEXT,
  company_postcode TEXT,
  company_tel   TEXT,
  company_email TEXT,
  company_web   TEXT,
  gas_safe_no   TEXT,
  engineer_name TEXT,
  gas_id        TEXT,
  logo_image    TEXT,  -- base64 data URL (small logos)
  plan          TEXT NOT NULL DEFAULT 'lite',  -- lite | pro | proplus
  subscription_active BOOLEAN DEFAULT FALSE,
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  engineer_sig  TEXT,  -- base64 signature image
  invoice_counter INTEGER DEFAULT 1,
  quote_counter INTEGER DEFAULT 1,
  registered_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 2. CERTIFICATES — all gas safety records (GSC, BSR, LPG, etc.)
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS certificates (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  cert_type     TEXT NOT NULL,   -- gsc, bsr, bcc, wn, lpg, cgs, catering, uhw, leisure, dsr, etc.
  file_ref      TEXT,            -- user-defined file reference
  data          JSONB NOT NULL,  -- full certificate form data (flexible schema)
  status        TEXT DEFAULT 'complete',  -- draft | complete
  saved_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  synced_from   TEXT             -- device identifier for conflict resolution
);

-- Index for fast lookups by user + date
CREATE INDEX IF NOT EXISTS idx_certs_user_date ON certificates(user_id, saved_at DESC);
CREATE INDEX IF NOT EXISTS idx_certs_type ON certificates(user_id, cert_type);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 3. INVOICES
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS invoices (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  invoice_number TEXT,
  data          JSONB NOT NULL,
  saved_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_invoices_user ON invoices(user_id, saved_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 4. QUOTES
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS quotes (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  quote_number  TEXT,
  data          JSONB NOT NULL,
  saved_at      TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quotes_user ON quotes(user_id, saved_at DESC);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 5. CONTACTS — client address book
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS contacts (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name          TEXT,
  company       TEXT,
  email         TEXT,
  phone         TEXT,
  address       TEXT,
  postcode      TEXT,
  notes         TEXT,
  data          JSONB,  -- any extra fields from VCF imports
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contacts_user ON contacts(user_id);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 6. ACCOUNT REPORTS — monthly bank statement analysis
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS account_reports (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  data          JSONB NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_account_reports_user ON account_reports(user_id);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 7. GSC FOLDERS — certificate grouping
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS gsc_folders (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  data          JSONB NOT NULL,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_gsc_folders_user ON gsc_folders(user_id);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 8. SUPPORT TICKETS
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS support_tickets (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  ticket_ref    TEXT NOT NULL,
  ticket_type   TEXT,
  screen        TEXT,
  description   TEXT,
  steps_to_reproduce TEXT,
  contact_email TEXT,
  contact_name  TEXT,
  username      TEXT,
  status        TEXT DEFAULT 'open',  -- open | in_progress | resolved | closed
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 9. APPLIANCE MEMORY — learned makes/models for autocomplete
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS appliance_memory (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  data          JSONB NOT NULL DEFAULT '{}',
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 10. EXPENSE CATEGORIES — learned expense categories for bank analysis
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS expense_categories (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  data          JSONB NOT NULL DEFAULT '{}',
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- 11. CUSTOM LOCATIONS — user-defined location options
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE TABLE IF NOT EXISTS custom_locations (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  locations     JSONB NOT NULL DEFAULT '[]',
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id)
);


-- ═══════════════════════════════════════════════════════════════════════════════
-- ROW-LEVEL SECURITY — each user can only access their own data
-- ═══════════════════════════════════════════════════════════════════════════════

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE gsc_folders ENABLE ROW LEVEL SECURITY;
ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE appliance_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE expense_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE custom_locations ENABLE ROW LEVEL SECURITY;

-- Profiles: users can read/write their own profile
CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON profiles FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = user_id);

-- Certificates: users can CRUD their own certs
CREATE POLICY "Users can view own certs" ON certificates FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own certs" ON certificates FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own certs" ON certificates FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own certs" ON certificates FOR DELETE USING (auth.uid() = user_id);

-- Invoices
CREATE POLICY "Users can view own invoices" ON invoices FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own invoices" ON invoices FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own invoices" ON invoices FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own invoices" ON invoices FOR DELETE USING (auth.uid() = user_id);

-- Quotes
CREATE POLICY "Users can view own quotes" ON quotes FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own quotes" ON quotes FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own quotes" ON quotes FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own quotes" ON quotes FOR DELETE USING (auth.uid() = user_id);

-- Contacts
CREATE POLICY "Users can view own contacts" ON contacts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own contacts" ON contacts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own contacts" ON contacts FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own contacts" ON contacts FOR DELETE USING (auth.uid() = user_id);

-- Account Reports
CREATE POLICY "Users can view own reports" ON account_reports FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own reports" ON account_reports FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own reports" ON account_reports FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own reports" ON account_reports FOR DELETE USING (auth.uid() = user_id);

-- GSC Folders
CREATE POLICY "Users can view own folders" ON gsc_folders FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own folders" ON gsc_folders FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own folders" ON gsc_folders FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own folders" ON gsc_folders FOR DELETE USING (auth.uid() = user_id);

-- Support Tickets — users can view their own, insert new ones
CREATE POLICY "Users can view own tickets" ON support_tickets FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert tickets" ON support_tickets FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own tickets" ON support_tickets FOR UPDATE USING (auth.uid() = user_id);

-- Appliance Memory
CREATE POLICY "Users can view own appliance memory" ON appliance_memory FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can upsert own appliance memory" ON appliance_memory FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own appliance memory" ON appliance_memory FOR UPDATE USING (auth.uid() = user_id);

-- Expense Categories
CREATE POLICY "Users can view own expense categories" ON expense_categories FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can upsert own expense categories" ON expense_categories FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own expense categories" ON expense_categories FOR UPDATE USING (auth.uid() = user_id);

-- Custom Locations
CREATE POLICY "Users can view own locations" ON custom_locations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can upsert own locations" ON custom_locations FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own locations" ON custom_locations FOR UPDATE USING (auth.uid() = user_id);


-- ═══════════════════════════════════════════════════════════════════════════════
-- ADMIN POLICY — your admin account can view all data
-- Replace 'YOUR_ADMIN_USER_ID' with your actual Supabase auth user ID after signup
-- ═══════════════════════════════════════════════════════════════════════════════
-- Uncomment and run after you know your admin user_id:
--
-- CREATE POLICY "Admin can view all certs" ON certificates FOR SELECT
--   USING (auth.uid() = 'YOUR_ADMIN_USER_ID'::uuid);
-- CREATE POLICY "Admin can view all profiles" ON profiles FOR SELECT
--   USING (auth.uid() = 'YOUR_ADMIN_USER_ID'::uuid);
-- CREATE POLICY "Admin can view all tickets" ON support_tickets FOR SELECT
--   USING (auth.uid() = 'YOUR_ADMIN_USER_ID'::uuid);


-- ═══════════════════════════════════════════════════════════════════════════════
-- HELPER: auto-update updated_at timestamp
-- ═══════════════════════════════════════════════════════════════════════════════
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables
CREATE TRIGGER set_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON certificates FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON invoices FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON quotes FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON account_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON gsc_folders FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON support_tickets FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON appliance_memory FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON expense_categories FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER set_updated_at BEFORE UPDATE ON custom_locations FOR EACH ROW EXECUTE FUNCTION update_updated_at();
