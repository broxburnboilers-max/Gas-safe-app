/**
 * fixtures/seed.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Helpers to seed localStorage before tests run.
 *
 * The app uses a key prefix based on the logged-in username:
 *   sk(key) → `${username}_${key}`
 *
 * We log in as "admin" so every key is prefixed "admin_".
 *
 * CRITICAL NOTES:
 * 1. Home screen buttons (New Job, Records, etc.) are PillBtn <div> elements —
 *    use :text() selectors, not button:has-text().
 * 2. The app shows ProfileSetupScreen if admin_user_profile is missing in
 *    localStorage when the App component mounts. Profile MUST be seeded
 *    before page.goto(), not after — use seedProfileBeforeLoad().
 * 3. Records are read from localStorage at App mount (useState init).
 *    Use seedRecordsBeforeLoad() to ensure records appear inside folder views.
 * 4. The RecordsScreen shows FOLDER CARDS first. Individual records only
 *    appear after clicking into a folder (Gas Safety Certificates, etc.).
 */

// ── Credentials ───────────────────────────────────────────────────────────────
export const ADMIN_EMAIL    = "admin";
export const ADMIN_PASSWORD = "WLG2026!";
export const USER_PREFIX    = "admin";

// ── Low-level localStorage helpers ────────────────────────────────────────────
export async function lsSet(page, key, value) {
  await page.evaluate(
    ([k, v]) => localStorage.setItem(k, v),
    [key, JSON.stringify(value)]
  );
}

export async function lsGet(page, key) {
  return page.evaluate((k) => {
    const raw = localStorage.getItem(k);
    return raw ? JSON.parse(raw) : null;
  }, key);
}

// ── Default profile data ───────────────────────────────────────────────────────
export const DEFAULT_PROFILE = {
  engineerName:       "Andrew Test",
  companyName:        "West Lothian Gas Ltd",
  gasSafeNo:          "123456",
  gasId:              "ENG001",
  companyAddr:        "1 Gas Street",
  companyPostcode:    "EH2 2BC",
  companyTel:         "01506000000",
  companyEmail:       "test@wlgas.co.uk",
  subscriptionActive: true,
};

// ── Seed profile via addInitScript before page load ───────────────────────────
// The App reads localStorage synchronously during useState() init.
// If the profile isn't there at mount time, it shows ProfileSetupScreen.
export async function seedProfileBeforeLoad(page, overrides = {}) {
  const profile = { ...DEFAULT_PROFILE, ...overrides };
  const key = `${USER_PREFIX}_user_profile`;
  await page.addInitScript(
    ([k, v]) => { try { localStorage.setItem(k, v); } catch {} },
    [key, JSON.stringify(profile)]
  );
  return profile;
}

// ── Seed GSC + BS records via addInitScript before page load ──────────────────
// Records are read at App mount (useState). Must be seeded before page.goto()
// to appear inside the Gas Safety Certificates and Boiler Service folders.
export async function seedRecordsBeforeLoad(page) {
  const savedAt = new Date().toISOString();

  const gscRecord = {
    certData: {
      tradingTitle:   "West Lothian Gas Ltd",
      engAddr:        "1 Gas Street",
      engPostcode:    "EH2 2BC",
      gasSafeNo:      "123456",
      engTel:         "01506000000",
      instAddr1:      "12 Test Street",
      instPostcode:   "EH1 1AB",
      instTel:        "07700900000",
      clientName:     "Test Customer",
      clientAddr1:    "12 Test Street",
      clientPostcode: "EH1 1AB",
      clientTel:      "07700900000",
      certRef:        "TEST-GSC-001",
      applianceMake:  "Baxi",
      applianceModel: "Platinum",
      applianceType:  "Boiler",
    },
    appliances: [],
    faults: [],
    finalChecks: { inspectionDate: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString() },
    signatureData: {},
    engineerData: { engineerName: "Andrew Test", gasSafeNo: "123456", certDate: new Date().toISOString() },
    savedAt,
  };

  const bsRecord = {
    type: "bs",
    serviceData: {
      certRef:      "TEST-BS-001",
      clientName:   "Test Customer",
      instAddr1:    "12 Test Street",
      instPostcode: "EH1 1AB",
      instTel:      "07700900000",
      make:         "Vaillant",
      model:        "ecoTEC",
      serialNo:     "VU123456",
      serviceDate:  new Date().toLocaleDateString("en-GB"),
    },
    bsEngData: {
      engineerName: "Andrew Test",
      gasSafeNo:    "123456",
      tradingTitle: "West Lothian Gas Ltd",
    },
    bsSigData: {},
    savedAt,
  };

  const key = `${USER_PREFIX}_gsc_records`;
  await page.addInitScript(
    ([k, gsc, bs]) => {
      try {
        const existing = JSON.parse(localStorage.getItem(k) || "[]");
        // Only add if not already seeded
        const hasSeed = existing.some(r => r.certData?.certRef === "TEST-GSC-001" || r.serviceData?.certRef === "TEST-BS-001");
        if (!hasSeed) {
          localStorage.setItem(k, JSON.stringify([...existing, gsc, bs]));
        }
      } catch {}
    },
    [key, gscRecord, bsRecord]
  );
}

// ── Navigate to login page ────────────────────────────────────────────────────
// The React app is at /app. The app checks window.location.hash === "#signin"
// at startup to go directly to the login form — navigate to /app#signin.
export async function goToLogin(page) {
  await page.goto("/app#signin");
  await page.waitForSelector('input[type="email"]', { timeout: 20_000 });
}

// ── Wait for home screen ──────────────────────────────────────────────────────
export async function waitForHome(page) {
  // "New Job" is a PillBtn <div> — use text selector
  await page.waitForSelector(':text("New Job")', { timeout: 25_000 });
}

// ── Full login flow ────────────────────────────────────────────────────────────
// seedProfileBeforeLoad() MUST be called before this if you want the home screen.
export async function login(page, email = ADMIN_EMAIL, password = ADMIN_PASSWORD) {
  await goToLogin(page);
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button:has-text("Sign In")');
  await waitForHome(page);
}

// ── Seed a client contact (after page load) ───────────────────────────────────
export async function seedContact(page, overrides = {}) {
  const contact = {
    id: "test-contact-1",
    name: "Test Customer",
    addr: "12 Test Street, Edinburgh",
    postcode: "EH1 1AB",
    tel: "07700900000",
    email: "testcustomer@example.com",
    ...overrides,
  };
  const existing = (await lsGet(page, `${USER_PREFIX}_client_contacts`)) || [];
  const deduped = existing.filter((c) => c.id !== contact.id);
  await lsSet(page, `${USER_PREFIX}_client_contacts`, [...deduped, contact]);
  return contact;
}

// ── Seed profile after page load (for tests that don't need home screen immediately) ──
export async function seedProfile(page, overrides = {}) {
  const profile = { ...DEFAULT_PROFILE, ...overrides };
  await lsSet(page, `${USER_PREFIX}_user_profile`, profile);
  return profile;
}

// ── Seed a completed GSC record (after page load) ─────────────────────────────
// NOTE: Records seeded after login won't appear in the app's React state
// because records are read from localStorage at mount (useState init).
// Use seedRecordsBeforeLoad() for tests that need records to appear in folders.
export async function seedGscRecord(page, overrides = {}) {
  const savedAt = new Date().toISOString();
  const record = {
    certData: {
      tradingTitle:   "West Lothian Gas Ltd",
      engAddr:        "1 Gas Street",
      engPostcode:    "EH2 2BC",
      gasSafeNo:      "123456",
      engTel:         "01506000000",
      instAddr1:      "12 Test Street",
      instPostcode:   "EH1 1AB",
      instTel:        "07700900000",
      clientName:     "Test Customer",
      clientAddr:     "Test Customer, 12 Test Street",
      clientPostcode: "EH1 1AB",
      clientTel:      "07700900000",
      certRef:        "TEST-GSC-SEED",
      applianceMake:  "Baxi",
      applianceModel: "Platinum",
      applianceType:  "Boiler",
      inspectionDate: new Date().toLocaleDateString("en-GB"),
    },
    savedAt,
    ...overrides,
  };
  const existing = (await lsGet(page, `${USER_PREFIX}_gsc_records`)) || [];
  await lsSet(page, `${USER_PREFIX}_gsc_records`, [...existing, record]);
  return record;
}

// ── Seed a completed BS record (after page load) ──────────────────────────────
export async function seedBsRecord(page, overrides = {}) {
  const savedAt = new Date().toISOString();
  const record = {
    type: "bs",
    serviceData: {
      fileRef:      "TEST-BS-001",
      clientName:   "Test Customer",
      instAddr1:    "12 Test Street",
      instPostcode: "EH1 1AB",
      instTel:      "07700900000",
      make:         "Vaillant",
      model:        "ecoTEC",
      serialNo:     "VU123456",
      serviceDate:  new Date().toLocaleDateString("en-GB"),
    },
    bsEngData: {
      engineerName: "Andrew Test",
      gasSafeNo:    "123456",
      tradingTitle: "West Lothian Gas Ltd",
    },
    bsSigData: {},
    savedAt,
    ...overrides,
  };
  const existing = (await lsGet(page, `${USER_PREFIX}_gsc_records`)) || [];
  await lsSet(page, `${USER_PREFIX}_gsc_records`, [...existing, record]);
  return record;
}
