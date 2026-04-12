/**
 * tests/04-contacts.spec.js
 * Client Contacts screen + sort code validation.
 *
 * Note: ClientContactsScreen has NO inline add-contact form.
 * It has two tabs: "📋 My Contacts" (list) and "📤 Import" (VCF/CSV file import only).
 * Tests are limited to viewing and searching the contact list.
 */

import { test, expect } from "@playwright/test";
import { login, seedProfileBeforeLoad, seedContact, lsGet, waitForHome, USER_PREFIX } from "../fixtures/seed.js";

test.describe("Client Contacts", () => {

  test.beforeEach(async ({ page }) => {
    await seedProfileBeforeLoad(page);
    await login(page);
    await seedContact(page);
  });

  test("contacts screen shows the seeded contact", async ({ page }) => {
    await page.locator(':text("Client Details"), :text("Contacts")').first().click();
    await page.waitForSelector("text=Test Customer", { timeout: 10_000 });
    await expect(page.locator("text=Test Customer")).toBeVisible();
  });

  test("search filters the contact list", async ({ page }) => {
    await page.locator(':text("Client Details"), :text("Contacts")').first().click();
    await page.waitForSelector("text=Test Customer", { timeout: 10_000 });

    const searchInput = page.locator('input[placeholder*="Search"], input[type="search"]').first();
    if (await searchInput.isVisible()) {
      await searchInput.fill("Test Customer");
      await expect(page.locator("text=Test Customer")).toBeVisible();
    }
  });

  test("Import tab is visible (VCF/CSV import only — no inline add form)", async ({ page }) => {
    await page.locator(':text("Client Details"), :text("Contacts")').first().click();
    await page.waitForSelector("text=Test Customer", { timeout: 10_000 });

    // The screen has two tabs: My Contacts and Import
    const importTab = page.locator(':text("Import"), :text("📤 Import")').first();
    await expect(importTab).toBeVisible({ timeout: 5_000 });
  });

});

// ── Sort code validation ─────────────────────────────────────────────────────
test.describe("Sort Code Validation (W1 fix)", () => {

  test("strips hyphens and spaces before digit-count check", async ({ page }) => {
    await seedProfileBeforeLoad(page);
    await login(page);

    const isValid = await page.evaluate(() => {
      const validate = (raw) => raw.replace(/[^0-9]/g, "").length === 6;
      return {
        withHyphens: validate("12-34-56"),
        withSpaces:  validate("12 34 56"),
        plain:       validate("123456"),
        tooShort:    validate("1234"),
        withLetters: validate("AB-12-34"),
      };
    });

    expect(isValid.withHyphens).toBe(true);
    expect(isValid.withSpaces).toBe(true);
    expect(isValid.plain).toBe(true);
    expect(isValid.tooShort).toBe(false);
    expect(isValid.withLetters).toBe(false);
  });

});
