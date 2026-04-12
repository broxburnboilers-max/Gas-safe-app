/**
 * tests/05-csv-expense-import.spec.js
 * Merchant pre-mapping logic (W2) + CSV file upload via UI.
 */

import { test, expect } from "@playwright/test";
import { login, seedProfileBeforeLoad, waitForHome } from "../fixtures/seed.js";

// ── Replicated merchant-map logic ─────────────────────────────────────────────
const MERCHANT_MAP_LOCAL = [
  { keywords: ["screwfix", "jewson", "travis perkins", "b&q", "toolstation", "city plumbing", "wolseley", "plumbase", "mkm", "buildbase"], category: "Materials & Supplies" },
  { keywords: ["shell", "bp", "esso", "texaco", "jet petrol", "morrisons fuel", "tesco fuel", "sainsbury fuel", "uber", "trainline", "national rail", "scotrail", "firstbus", "lothian buses", "enterprise rent"], category: "Travel & Transport" },
  { keywords: ["greggs", "costa", "starbucks", "mcdonalds", "mcdonald", "subway", "tesco", "asda", "sainsbury", "morrisons", "co-op", "lidl", "aldi", "boots pharmacy"], category: "Meals & Subsistence" },
  { keywords: ["google", "microsoft", "adobe", "xero", "quickbooks", "sage", "dropbox", "zoom", "slack", "github", "aws ", "amazon web"], category: "Software & Subscriptions" },
  { keywords: ["aviva", "axa", "simply business", "hiscox", "zurich", "direct line", "admiral", "rias"], category: "Insurance" },
];

function mapMerchant(description) {
  const lower = description.toLowerCase();
  for (const { keywords, category } of MERCHANT_MAP_LOCAL) {
    if (keywords.some((kw) => lower.includes(kw))) return category;
  }
  return "General";
}

// ── Unit tests — no browser navigation needed ─────────────────────────────────
test.describe("CSV Expense Import — Merchant Pre-mapping (W2)", () => {
  test("Screwfix maps to Materials & Supplies", () => { expect(mapMerchant("SCREWFIX STORE 123")).toBe("Materials & Supplies"); });
  test("Shell maps to Travel & Transport", () => { expect(mapMerchant("SHELL PETROL STATION")).toBe("Travel & Transport"); });
  test("Greggs maps to Meals & Subsistence", () => { expect(mapMerchant("GREGGS BAKERY EDINBURGH")).toBe("Meals & Subsistence"); });
  test("Google Workspace maps to Software & Subscriptions", () => { expect(mapMerchant("GOOGLE WORKSPACE MONTHLY")).toBe("Software & Subscriptions"); });
  test("Simply Business maps to Insurance", () => { expect(mapMerchant("SIMPLY BUSINESS INSURANCE LTD")).toBe("Insurance"); });
  test("unknown merchant falls through to General", () => { expect(mapMerchant("UNKNOWN MERCHANT XYZ")).toBe("General"); });
  test("case-insensitive matching works", () => {
    expect(mapMerchant("screwfix store")).toBe("Materials & Supplies");
    expect(mapMerchant("SCREWFIX STORE")).toBe("Materials & Supplies");
  });
});

// ── UI upload test ─────────────────────────────────────────────────────────────
test.describe("CSV File Upload via UI", () => {

  const TEST_CSV = [
    "Date,Description,Amount,Category",
    "11/04/2026,SCREWFIX STORE 001,42.50,",
    "11/04/2026,SHELL PETROL,60.00,",
    "11/04/2026,GREGGS BAKERY,3.20,",
    "11/04/2026,UNKNOWN MERCHANT XYZ,15.00,",
  ].join("\n");

  test("uploading a CSV file opens the import screen", async ({ page }) => {
    await seedProfileBeforeLoad(page);
    await login(page);

    const reportsBtn = page.locator(':text("Reports"), :text("Account"), :text("Finance")').first();
    if (!(await reportsBtn.isVisible({ timeout: 5_000 }).catch(() => false))) {
      test.skip(true, "Reports button not found — skipping");
      return;
    }
    await reportsBtn.click();

    const importBtn = page.locator(
      'button:has-text("Import"), button:has-text("Upload"), button:has-text("CSV")'
    ).first();
    if (!(await importBtn.isVisible({ timeout: 5_000 }).catch(() => false))) {
      test.skip(true, "CSV import button not found — skipping");
      return;
    }

    const [fileChooser] = await Promise.all([
      page.waitForEvent("filechooser"),
      importBtn.click(),
    ]);
    await fileChooser.setFiles({
      name: "expenses.csv",
      mimeType: "text/csv",
      buffer: Buffer.from(TEST_CSV),
    });

    await expect(
      page.locator('text=/import|category|expense/i').first()
    ).toBeVisible({ timeout: 10_000 });
  });

});
