// playwright.config.js
// Gas Safe App — Playwright test configuration
// Run against the live Netlify deployment or a local dev server.
//
// Usage:
//   npx playwright test                        <- run all tests
//   npx playwright test --headed               <- watch the browser
//   npx playwright test tests/login.spec.js    <- single file
//   BASE_URL=http://localhost:5173 npx playwright test  <- local dev
//
// NOTE: Mobile Safari (WebKit) is excluded — install it with:
//   npx playwright install webkit
// then uncomment the Mobile Safari project below.

import { defineConfig, devices } from "@playwright/test";

// NOTE: The React app lives at /app — the root URL is now a static marketing page.
// Tests navigate to /app (or /app#signin) explicitly.
// For local dev: BASE_URL=http://localhost:5173 npx playwright test
const BASE_URL = process.env.BASE_URL || "https://gas-safety-app.com";

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,          // 60 s per test (PDF generation can be slow)
  retries: 1,               // one automatic retry on flake
  reporter: [["list"], ["html", { open: "never", outputFolder: "test-report" }]],

  use: {
    baseURL: BASE_URL,
    headless: true,
    viewport: { width: 390, height: 844 },  // iPhone 14 Pro — primary use-case
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "retain-on-failure",
    ignoreHTTPSErrors: true,
  },

  projects: [
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 7"] },
    },
    {
      name: "Desktop Chrome",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 900 } },
    },
    // Uncomment this block after running: npx playwright install webkit
    // {
    //   name: "Mobile Safari",
    //   use: { ...devices["iPhone 14"] },
    // },
  ],
});
