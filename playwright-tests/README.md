# Gas Safe App — Playwright Tests

Automated end-to-end and unit-style tests for the Gas Safe App.  
Tests run against the live Netlify deployment by default, or any local dev server.

---

## Quick Start

### 1. Install

```bash
cd playwright-tests
npm install
npx playwright install --with-deps chromium
```

> `--with-deps` installs the system libraries Playwright needs.  
> Add `firefox webkit` to that command if you want those browsers too.

### 2. Run all tests (headless)

```bash
npm test
```

### 3. Watch the browser (useful for debugging)

```bash
npm run test:headed
```

### 4. Interactive UI mode

```bash
npm run test:ui
```

This opens Playwright's visual dashboard — you can run individual tests, see timelines, and inspect screenshots.

---

## Test Against a Local Dev Server

```bash
BASE_URL=http://localhost:5173 npm test
```

Start your Vite dev server first:

```bash
cd C:\Users\Andrew\Documents\gas-safety-multiuser
npm run dev
```

---

## Test Files

| File | What it tests |
|------|--------------|
| `tests/01-login.spec.js` | Auth flow — landing, `#signin` hash, wrong password, correct login, logout |
| `tests/02-boiler-service.spec.js` | Full BS wizard — all 8 steps, save, verify in Records |
| `tests/03-records-and-pdf.spec.js` | Records screen, PDF preview opens, Combine Certs button visible |
| `tests/04-contacts.spec.js` | Client contacts list, add contact, search filter, sort code validation (W1) |
| `tests/05-csv-expense-import.spec.js` | Merchant pre-mapping logic (W2) + CSV file upload via UI |
| `tests/06-offline-pdf-error.spec.js` | CDN blocked → friendly error message shown (LOW fix) |
| `tests/07-mobile-layout.spec.js` | Mobile viewport — no horizontal overflow, all buttons reachable |

---

## fixtures/seed.js

A helper library that seeds localStorage before each test so you don't have to
fill forms to get to the state you want to test.

```js
import { login, seedContact, seedGscRecord, seedBsRecord } from "../fixtures/seed.js";

// Log in as admin
await login(page);

// Add a contact directly to localStorage
await seedContact(page, { name: "Mrs Smith", postcode: "G1 2AB" });

// Add a pre-built GSC record
await seedGscRecord(page);
```

**Credentials used:**
- Username: `admin`
- Password: `WLG2026!`

Change these in `fixtures/seed.js` if you create a dedicated test user.

---

## Viewing Results

After a run, open the HTML report:

```bash
npm run test:report
```

Screenshots and traces for failed tests are saved automatically to `test-report/`.

---

## Adding a New Test

1. Create `tests/08-my-feature.spec.js`
2. Import `login` and any seed helpers you need
3. Write `test()` blocks using `expect()` assertions
4. Run with `npm test`

Playwright's [locator docs](https://playwright.dev/docs/locators) are the best reference.

---

## Running on BrowserStack (optional)

If you want to run these tests on real devices via BrowserStack:

1. Install: `npm install @browserstack/playwright-browserstack -D`
2. Set env vars: `BROWSERSTACK_USERNAME` and `BROWSERSTACK_ACCESS_KEY`
3. Update `playwright.config.js` to use the BrowserStack CDP endpoint

Full guide: https://www.browserstack.com/docs/automate/playwright

---

## Known Limitations

- **PDF download can't be intercepted in headless mode** — tests verify the UI reaches the preview state rather than asserting the downloaded file's contents.
- **Signature canvas** — drawing on a canvas in headless mode is unreliable; signature steps are skipped in the wizard test.
- **Combined PDF rendering** is slow (10–20 s) — the 60 s `timeout` in config covers this.
