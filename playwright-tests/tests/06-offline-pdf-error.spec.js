/**
 * tests/06-offline-pdf-error.spec.js
 * Verifies the friendly offline error when CDN libraries can't load.
 *
 * When CDN scripts are blocked, PDFPreview.downloadPDF() catches the script
 * load error and calls:
 *   alert("Could not generate PDF: ...")
 *
 * The error thrown when html2canvas/jsPDF scripts fail to load is a browser
 * Event object (not an Error), so the alert message may be:
 *   "Could not generate PDF: [object Event]"  — or similar
 *
 * We intercept the dialog event rather than look for DOM text.
 *
 * Navigation path: Records hub → Gas Safety Certificates folder →
 *   record card click → action sheet → Preview → Download PDF button →
 *   alert dialog appears.
 */

import { test, expect } from "@playwright/test";
import { login, seedProfileBeforeLoad, seedRecordsBeforeLoad } from "../fixtures/seed.js";

test.describe("Offline PDF Error Handling (LOW fix)", () => {

  test("shows friendly error when CDN libraries are blocked", async ({ page }) => {
    // Capture the alert dialog — PDFPreview uses alert() for PDF errors
    let dialogMessage = null;
    page.on("dialog", async (dialog) => {
      dialogMessage = dialog.message();
      await dialog.accept();
    });

    // Block CDN requests before loading the page
    await page.route("**cdnjs.cloudflare.com**", (route) => route.abort());
    await page.route("**unpkg.com**", (route) => route.abort());
    await page.route("**cdn.jsdelivr.net**", (route) => route.abort());

    // Seed profile and records before page load
    await seedProfileBeforeLoad(page);
    await seedRecordsBeforeLoad(page);
    await login(page);

    // Navigate: Records hub → Gas Safety Certificates folder
    await page.locator(':text("Records")').first().click();
    await page.waitForSelector('text=/Gas Safety Certificates/i', { timeout: 10_000 });
    await page.locator('text=/Gas Safety Certificates/i').first().click();

    // Wait for individual record cards
    await page.waitForSelector('text=/Test Customer|TEST-GSC-001/i', { timeout: 10_000 });

    // Tap record card to open action sheet
    await page.locator('text=/Test Customer|TEST-GSC-001/i').first().click();

    // Click "👁 Preview" in the bottom sheet
    await page.waitForSelector(':text("Preview")', { timeout: 8_000 });
    await page.locator(':text("Preview")').first().click();

    // Wait for PDFPreview screen then click the Download PDF button
    await page.waitForSelector(':text("PDF Preview")', { timeout: 8_000 });
    await page.locator('button:has-text("Download PDF")').first().click();

    // Wait for the dialog to fire (CDN blocked → script onerror → catch → alert)
    // The dialog handler fires asynchronously; poll for up to 15 seconds
    await expect.poll(
      () => dialogMessage,
      { timeout: 15_000, message: "Expected an alert dialog from PDFPreview when CDN is blocked" }
    ).not.toBeNull();

    // The alert should mention a PDF error (exact text depends on browser Event serialisation)
    expect(dialogMessage).toMatch(/could not generate pdf|pdf error|requires an internet connection|internet connection|offline|could not load/i);
  });

});
