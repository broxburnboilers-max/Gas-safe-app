// ═══════════════════════════════════════════════════════════════════════════════
// Citizen Gas Importer — Auto-import Gas Safety Cert emails sent from
// the Citizen Gas app into Gas Safe Records.
//
// Flow:
//   1. Search Gmail for Citizen Gas cert emails (last 30 days)
//   2. Skip already-imported message IDs
//   3. For each new message: extract plaintext + image attachments
//   4. Parse via parseGSCEmailTemplate (passed in to avoid circular dep)
//   5. Rename photos per property + function (e.g. "23 Station Rd cooker cap")
//   6. Bundle into a date-named gscFolder
//   7. Return { folder, records, importedIds } for the App to merge into state
// ═══════════════════════════════════════════════════════════════════════════════

import { gmailFetch } from "./gmailAuth";

const IMPORTED_IDS_KEY = "wlg_citizen_imported_msg_ids";
const SEARCH_QUERY = [
  // Match either source — emails were originally going to westlothiangas, now broxburnboilers
  '(from:westlothiangas@gmail.com OR from:broxburnboilers@gmail.com OR to:broxburnboilers@gmail.com)',
  // Citizen Gas template subject
  '(subject:"Gas Safety" OR subject:"Citizen Gas" OR subject:"PROPERTY")',
  'newer_than:30d',
].join(' ');

// ─── Imported-IDs tracking ───────────────────────────────────────────────────
function getImportedIds() {
  try { return new Set(JSON.parse(localStorage.getItem(IMPORTED_IDS_KEY) || "[]")); }
  catch { return new Set(); }
}

function saveImportedIds(set) {
  try { localStorage.setItem(IMPORTED_IDS_KEY, JSON.stringify([...set])); } catch {}
}

// ─── Base64URL → string (for plaintext bodies) ──────────────────────────────
function b64UrlDecodeText(b64url) {
  const b64 = b64url.replace(/-/g, "+").replace(/_/g, "/");
  try {
    const bin = atob(b64);
    // Try UTF-8 decode
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return new TextDecoder("utf-8").decode(bytes);
  } catch { return ""; }
}

// ─── Walk MIME tree to collect text body + image attachments ────────────────
function collectParts(payload, out) {
  if (!payload) return;
  const mimeType = payload.mimeType || "";
  const filename = payload.filename || "";
  const body = payload.body || {};

  if (mimeType === "text/plain" && body.data && !out.text) {
    out.text = b64UrlDecodeText(body.data);
  } else if (mimeType === "text/html" && body.data && !out.html) {
    out.html = b64UrlDecodeText(body.data);
  } else if (mimeType.startsWith("image/") && filename) {
    out.imageParts.push({
      filename,
      mimeType,
      attachmentId: body.attachmentId || null,
      data: body.data || null,
      partId: payload.partId,
    });
  }

  if (Array.isArray(payload.parts)) {
    for (const p of payload.parts) collectParts(p, out);
  }
}

// ─── Strip HTML to plain text (fallback when no text/plain part) ────────────
function htmlToText(html) {
  if (!html) return "";
  const tmp = document.createElement("div");
  tmp.innerHTML = html.replace(/<br\s*\/?>/gi, "\n").replace(/<\/p>/gi, "\n");
  return (tmp.textContent || tmp.innerText || "").replace(/\n{3,}/g, "\n\n");
}

// ─── Fetch attachment data ──────────────────────────────────────────────────
async function fetchAttachment(messageId, part) {
  if (part.data) return part.data; // already inline
  if (!part.attachmentId) return null;
  const r = await gmailFetch(`/gmail/v1/users/me/messages/${messageId}/attachments/${part.attachmentId}`);
  return r.data || null;
}

// ─── Convert base64url payload to data URL ──────────────────────────────────
function toDataUrl(b64url, mimeType) {
  // Gmail returns base64url; convert to standard base64 for data URL
  const b64 = b64url.replace(/-/g, "+").replace(/_/g, "/");
  return `data:${mimeType};base64,${b64}`;
}

// ─── Generate photo names per property + function ──────────────────────────
const PHOTO_FUNCTIONS = ["cooker cap", "Tightness test", "gas works doc", "gas isolation doc"];

function shortAddress(record) {
  // Prefer install address if available, fall back to certRef
  const addr = (record.instAddr1 || record.clientAddr1 || record.certRef || "Property").trim();
  // Strip trailing postcode and city pollution; keep first comma-separated chunk
  const firstChunk = addr.split(",")[0].trim();
  return firstChunk.replace(/[\\/:*?"<>|]/g, "").slice(0, 60) || "Property";
}

function namePhotosForRecord(record, photos) {
  // Map photos in order: cookerCap, tightness, gasWorks, gasIsolation
  // Only include functions where the parser flagged a photo OR where the field has content
  const wanted = [];
  if (record.cookerCappedPhoto || record.cookerCapped) wanted.push("cooker cap");
  if (record.tightnessTestPhoto || record.tightnessTestResult) wanted.push("Tightness test");
  if (record.gasWorksDocPhoto || record.gasWorksDoc) wanted.push("gas works doc");
  if (record.gasIsolationDocPhoto || record.gasIsolationDoc) wanted.push("gas isolation doc");
  // If parser found nothing flagged, fall back to default order so we still name something sensible
  const fns = wanted.length > 0 ? wanted : PHOTO_FUNCTIONS;
  const addr = shortAddress(record);
  return photos.slice(0, fns.length).map((p, i) => ({
    name: `${addr} ${fns[i]}`,
    dataUrl: p.dataUrl,
    mimeType: p.mimeType,
  }));
}

// ─── Main importer ──────────────────────────────────────────────────────────
/**
 * Import new Citizen Gas certs from Gmail.
 * @param {Function} parseGSCEmailTemplate - the parser exported from App.jsx
 * @param {Function} onProgress - optional (msg) => void for UI feedback
 * @returns {Promise<{folder, records, skipped, errors}>}
 */
export async function importCitizenGasFromGmail(parseGSCEmailTemplate, onProgress) {
  const log = (m) => { if (onProgress) onProgress(m); };
  log("Searching Gmail…");

  // 1) List matching messages
  const list = await gmailFetch(`/gmail/v1/users/me/messages?q=${encodeURIComponent(SEARCH_QUERY)}&maxResults=50`);
  const messages = list.messages || [];
  log(`Found ${messages.length} matching email(s)`);

  const importedIds = getImportedIds();
  const newMessages = messages.filter(m => !importedIds.has(m.id));
  if (newMessages.length === 0) {
    return { folder: null, records: [], skipped: messages.length, errors: [] };
  }

  // 2) Fetch each message + parse
  const allRecords = [];
  const errors = [];

  for (const msg of newMessages) {
    try {
      log(`Fetching message ${msg.id.slice(0, 8)}…`);
      const full = await gmailFetch(`/gmail/v1/users/me/messages/${msg.id}?format=full`);
      const out = { text: "", html: "", imageParts: [] };
      collectParts(full.payload, out);
      const bodyText = out.text || htmlToText(out.html);
      if (!bodyText.trim()) {
        errors.push({ id: msg.id, err: "no text body" });
        continue;
      }

      // 3) Parse cert(s) from body
      const certs = parseGSCEmailTemplate(bodyText);
      if (!certs || certs.length === 0) {
        errors.push({ id: msg.id, err: "parser returned no certs" });
        continue;
      }

      // 4) Fetch image attachments and convert to data URLs
      log(`Downloading ${out.imageParts.length} photo(s)…`);
      const photos = [];
      for (const p of out.imageParts) {
        const data = await fetchAttachment(msg.id, p);
        if (data) photos.push({ dataUrl: toDataUrl(data, p.mimeType), mimeType: p.mimeType });
      }

      // 5) Distribute photos across certs (most common case: 1 cert per email)
      // If multiple certs in one email, split photos by 4-per-cert
      const PHOTOS_PER_CERT = 4;
      certs.forEach((cert, idx) => {
        const start = idx * PHOTOS_PER_CERT;
        const slice = photos.slice(start, start + PHOTOS_PER_CERT);
        const named = namePhotosForRecord(cert, slice);

        // Tag the cert with metadata so it lands in the right place
        cert.certType = cert.certType || "gsc";
        cert.type = cert.type || "gsc";
        cert.savedAt = new Date().toISOString();
        cert.fileRef = cert.certRef || `Citizen-${msg.id.slice(0, 8)}-${idx}`;
        cert.photos = named;
        cert.importedFromCitizenGas = true;
        cert.sourceMessageId = msg.id;
        allRecords.push(cert);
      });

      importedIds.add(msg.id);
    } catch (e) {
      errors.push({ id: msg.id, err: e.message || String(e) });
    }
  }

  // 6) Build folder name from today's date (the certificate batch date)
  const today = new Date();
  const folderName = `Citizen Gas — ${today.toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })}`;
  const folder = {
    id: `cg_${today.toISOString().slice(0, 10)}_${Math.random().toString(36).slice(2, 6)}`,
    name: folderName,
    createdAt: today.toISOString(),
  };

  // Stamp folder ID onto each record
  for (const r of allRecords) r.gscFolder = folder.id;

  saveImportedIds(importedIds);

  return { folder, records: allRecords, skipped: messages.length - newMessages.length, errors };
}

// ─── Reset (for debugging) ─────────────────────────────────────────────────
export function resetCitizenGasImportHistory() {
  try { localStorage.removeItem(IMPORTED_IDS_KEY); } catch {}
}
