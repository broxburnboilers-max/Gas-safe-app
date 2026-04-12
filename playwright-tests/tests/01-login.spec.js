/**
 * tests/01-login.spec.js
 * Authentication flow tests.
 */

import { test, expect } from "@playwright/test";
import { goToLogin, login, waitForHome, seedProfileBeforeLoad } from "../fixtures/seed.js";

test.describe("Authentication", () => {

  test("landing page has a Sign In button", async ({ page }) => {
    // The React app is at /app (root / is now a static marketing page)
    await page.goto("/app");
    // Wait for any button to appear (confirms React has mounted)
    await page.waitForSelector("button", { timeout: 20_000 });
    // LandingScreen header has a button with exact text "Sign In".
    // Use :text-is() for exact match to avoid "Sign In to Existing Account".
    await expect(page.locator('button:text-is("Sign In")').first()).toBeVisible({ timeout: 10_000 });
  });

  test("clicking Sign In shows the login form", async ({ page }) => {
    await goToLogin(page);
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test("wrong password shows an error message", async ({ page }) => {
    await goToLogin(page);
    await page.fill('input[type="email"]', "admin");
    await page.fill('input[type="password"]', "wrongpassword");
    await page.click('button:has-text("Sign In")');
    await expect(
      page.locator("text=/invalid|incorrect|wrong|not found/i")
    ).toBeVisible({ timeout: 10_000 });
  });

  test("correct credentials reach the home screen", async ({ page }) => {
    await seedProfileBeforeLoad(page);
    await login(page);
    await expect(page.locator(':text("New Job")')).toBeVisible();
  });

  test("logout returns to the landing/login screen", async ({ page }) => {
    await seedProfileBeforeLoad(page);
    await login(page);
    const logoutBtn = page.locator(':text("Logout"), :text("Sign Out"), :text("Log out")').first();
    await logoutBtn.click();
    // After logout, LandingScreen shows — check for the header "Sign In" button
    await expect(
      page.locator('button:text-is("Sign In")').first()
    ).toBeVisible({ timeout: 10_000 });
  });

});
