/**
 * tests/03-records-and-pdf.spec.js
 * Seeds records into localStorage BEFORE page load, then navigates the
 * full path: Records hub → Gas Safety Certificates folder → record card
 * → action sheet → Preview → PDF preview screen.
 *
 * KEY FACTS:
 * - Records are read from localStorage at App mount (useState init).
 *   Must use seedRecordsBeforeLoad() so they appear in folder views.
 * - RecordsScreen shows FOLDER CARDS, not individual records.
 *   Must click "Gas Safety Certificates" folder to see individual GSC cards.
 * - Clicking a record card opens a bottom ACTION SHEET (not the preview directly).
 *   Must click "👁 Preview" in the sheet to open PDFPreview.
 * - PDFPreview shows a "PDF Preview" header span + "Download PDF" button.
 */

import { test, expect } from "@playwright/test";
import { login, seedProfileBeforeLoad, seedRecordsBeforeLoad } from "../fixtures/seed.js";

test.describe("Records Screen & PDF Preview", () => {

  test.beforeEach(async ({ page }) => {
    // All three must be called before page load (addInitScript)
    await seedProfileBeforeLoad(page);
    await seedRecordsBeforeLoad(page);
    await login(page);
  });

  test("records screen lists seeded certificates", async ({ page }) => {
    await page.locator(':text("Records")').first().click();
    // RecordsScreen shows folder cards — check folder card labels exist
    await page.waitForSelector('text=/Gas Safety Certificates|Boiler Service Records/i', { timeout: 10_000 });
    await expect(page.locator('text=/Gas Safety Certificates|Boiler Service Records/i').first()).toBeVisible();
  });

  test("tapping a record opens the detail / PDF preview screen", async ({ page }) => {
    // Navigate to Records hub
    await page.locator(':text("Records")').first().click();
    await page.waitForSelector('text=/Gas Safety Certificates/i', { timeout: 10_000 });

    // Click the "Gas Safety Certificates" folder card to enter it
    await page.locator('text=/Gas Safety Certificates/i').first().click();

    // Wait for individual record cards inside the folder
    // Each card shows the client name or cert ref
    await page.waitForSelector('text=/Test Customer|TEST-GSC-001/i', { timeout: 10_000 });

    // Tap the record card — this opens a bottom action sheet (sets selected state)
    await page.locator('text=/Test Customer|TEST-GSC-001/i').first().click();

    // Bottom sheet appears with "👁 Preview" action button
    await page.waitForSelector(':text("Preview")', { timeout: 8_000 });
    await page.locator(':text("Preview")').first().click();

    // PDFPreview screen shows "PDF Preview" in the sticky header
    await expect(
      page.locator(':text("PDF Preview"), :text("Gas Service/Breakdown Record"), button:has-text("Download PDF"), button:has-text("Download")').first()
    ).toBeVisible({ timeout: 15_000 });
  });

  test("home screen shows the Combine Certs option", async ({ page }) => {
    await expect(page.locator(':text("Combine")').first()).toBeVisible({ timeout: 10_000 });
  });

});
