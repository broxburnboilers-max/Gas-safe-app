// ═══════════════════════════════════════════════════════════════════════════════
// Gmail Auth — Google Identity Services token flow (pure client-side)
//
// Requires VITE_GOOGLE_CLIENT_ID in Netlify env (OAuth 2.0 Client ID, type: Web)
// with origin https://www.gas-safety-app.com authorised.
//
// Scope: gmail.readonly only — we never send/modify/delete email.
// ═══════════════════════════════════════════════════════════════════════════════

const GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.readonly";
const TOKEN_KEY = "wlg_gmail_token";
const GIS_SRC = "https://accounts.google.com/gsi/client";

let gisLoadedPromise = null;
let tokenClient = null;

function getClientId() {
  // Vite injects this at build time
  return (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_GOOGLE_CLIENT_ID) || "";
}

export function isGmailConfigured() {
  return !!getClientId();
}

function loadGIS() {
  if (gisLoadedPromise) return gisLoadedPromise;
  gisLoadedPromise = new Promise((resolve, reject) => {
    if (typeof window === "undefined") return reject(new Error("No window"));
    if (window.google?.accounts?.oauth2) return resolve(window.google);
    const existing = document.querySelector(`script[src="${GIS_SRC}"]`);
    if (existing) {
      existing.addEventListener("load", () => resolve(window.google));
      existing.addEventListener("error", reject);
      return;
    }
    const s = document.createElement("script");
    s.src = GIS_SRC;
    s.async = true;
    s.defer = true;
    s.onload = () => resolve(window.google);
    s.onerror = reject;
    document.head.appendChild(s);
  });
  return gisLoadedPromise;
}

function getCachedToken() {
  try {
    const raw = localStorage.getItem(TOKEN_KEY);
    if (!raw) return null;
    const t = JSON.parse(raw);
    if (!t?.access_token || !t?.expires_at) return null;
    if (Date.now() > t.expires_at - 60_000) return null; // 1-min buffer
    return t;
  } catch { return null; }
}

function saveToken(tokenResponse) {
  const expires_at = Date.now() + (tokenResponse.expires_in * 1000);
  const t = { access_token: tokenResponse.access_token, expires_at };
  try { localStorage.setItem(TOKEN_KEY, JSON.stringify(t)); } catch {}
  return t;
}

export function clearGmailToken() {
  try { localStorage.removeItem(TOKEN_KEY); } catch {}
}

/**
 * Get a Gmail access token. Tries cached token first; otherwise prompts user.
 * @param {boolean} interactive - if true, may show consent popup; if false, silent only
 * @returns {Promise<string|null>} access token, or null if silent failed
 */
export async function getGmailToken(interactive = true) {
  const cached = getCachedToken();
  if (cached) return cached.access_token;

  const clientId = getClientId();
  if (!clientId) throw new Error("Gmail not configured (missing VITE_GOOGLE_CLIENT_ID)");

  await loadGIS();
  const google = window.google;
  if (!google?.accounts?.oauth2) throw new Error("Google Identity Services failed to load");

  return new Promise((resolve, reject) => {
    if (!tokenClient) {
      tokenClient = google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: GMAIL_SCOPE,
        callback: () => {}, // overridden per-request
      });
    }
    tokenClient.callback = (resp) => {
      if (resp.error) {
        if (!interactive && resp.error === "interaction_required") return resolve(null);
        return reject(new Error(resp.error_description || resp.error));
      }
      const saved = saveToken(resp);
      resolve(saved.access_token);
    };
    try {
      tokenClient.requestAccessToken({ prompt: interactive ? "" : "none" });
    } catch (e) {
      reject(e);
    }
  });
}

/**
 * Authenticated Gmail API fetch. Returns parsed JSON.
 */
export async function gmailFetch(path, opts = {}) {
  const token = await getGmailToken(false) || await getGmailToken(true);
  if (!token) throw new Error("Gmail auth required");
  const url = path.startsWith("http") ? path : `https://gmail.googleapis.com${path}`;
  const r = await fetch(url, {
    ...opts,
    headers: { ...(opts.headers || {}), Authorization: `Bearer ${token}` },
  });
  if (r.status === 401) {
    clearGmailToken();
    throw new Error("Gmail token expired — please re-authorize");
  }
  if (!r.ok) {
    const text = await r.text().catch(() => "");
    throw new Error(`Gmail API ${r.status}: ${text.slice(0, 200)}`);
  }
  return r.json();
}
