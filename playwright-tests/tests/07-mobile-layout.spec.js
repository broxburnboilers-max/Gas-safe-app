/**
 * tests/07-mobile-layout.spec.js
 * Mobile layout sanity checks.
 */

import { test, expect } from "@playwright/test";
import { goToLogin, login, seedProfileBeforeLoad } from "../fixtures/seed.js";

// ── Tests that require being logged in ───────────────────────────────────────
test.describe("Mobile Layout Sanity", () => {

  test.beforeEach(async ({ page }) => {
    await seedProfileBeforeLoad(page);
    await login(page);
  });

  test("home screen pill buttons are all within the viewport", async ({ page }) => {
    // PillBtns render as <div> with borderRadius:999 (React camelCase).
    // Use getComputedStyle to find them — works on both Mobile + Desktop Chrome.
    const overflowing = await page.evaluate(() => {
      const vw = window.innerWidth;
      const allDivs = Array.from(document.querySelectorAll("div"));
      const pills = allDivs.filter(el => {
        const style = window.getComputedStyle(el);
        const br = style.borderRadius;
        return br && parseFloat(br) >= 100;
      });
      return pills.filter(el => {
        const box = el.getBoundingClientRect();
        return box.width > 50 && (box.right > vw + 2); // 2px tolerance
      }).length;
    });
    expect(overflowing).toBe(0);
  });

  test("New Job screen lists all job types without horizontal overflow", async ({ page }) => {
    await page.locator(':text("New Job")').first().click();
    await page.waitForSelector('text=/Boiler Service/i', { timeout: 8_000 });
    // Compare scrollWidth against actual viewport width (not a hardcoded 410)
    // to work on both Mobile Chrome (390px) and Desktop Chrome (1280px)
    const { bodyWidth, viewportWidth } = await page.evaluate(() => ({
      bodyWidth: document.body.scrollWidth,
      viewportWidth: window.innerWidth,
    }));
    // No horizontal overflow means scrollWidth should not exceed viewport width
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 2); // 2px tolerance
    await expect(page.locator('text=/Gas Test|Purging|LPG|Catering/i').first()).toBeAttached({ timeout: 5_000 });
  });

  test("boiler service step 1 viewport check", async ({ page }) => {
    // Navigate to New Job → click Boiler Service
    await page.locator(':text("New Job")').first().click();
    await page.waitForSelector('text=/Boiler Service/i', { timeout: 8_000 });
    await page.locator('button:has-text("Boiler Service")').first().click();

    // Wait briefly for navigation to settle
    await page.waitForTimeout(2_000);

    // Check for no horizontal overflow on whatever screen renders
    const { bodyWidth, viewportWidth } = await page.evaluate(() => ({
      bodyWidth: document.body.scrollWidth,
      viewportWidth: window.innerWidth,
    }));
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 2);
  });

});

// ── Login form test — must NOT use the login beforeEach ──────────────────────
// This test navigates to the landing page fresh so it can check the login form.
// It does NOT depend on being logged in first.
test.describe("Mobile Layout — Login Form", () => {

  test("login form inputs are not clipped on small screen", async ({ page }) => {
    // Navigate directly to "/" as a fresh unauthenticated user
    // (no seedProfileBeforeLoad — we don't need the home screen)
    await goToLogin(page);
    // goToLogin clicks "Sign In" and waits for email input — no navigation issues
    await page.waitForSelector('input[type="email"]', { timeout: 10_000 });
    const emailBox = await page.locator('input[type="email"]').boundingBox();
    const passBox  = await page.locator('input[type="password"]').boundingBox();
    expect(emailBox?.width).toBeGreaterThan(200);
    expect(passBox?.width).toBeGreaterThan(200);
  });

});
