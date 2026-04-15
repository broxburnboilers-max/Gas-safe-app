// ═══════════════════════════════════════════════════════════════════════════════
// Sync Engine — Offline-first localStorage ↔ Supabase sync
//
// Strategy: localStorage is the source of truth on each device.
// When online, changes are pushed to Supabase in the background.
// On login/app start, cloud data is pulled and merged with local.
// ═══════════════════════════════════════════════════════════════════════════════
import { supabase, isSupabaseEnabled } from './supabaseClient';

// ─── Queue for offline writes ────────────────────────────────────────────────
const SYNC_QUEUE_KEY = 'wlg_sync_queue';

function getSyncQueue() {
  try { return JSON.parse(localStorage.getItem(SYNC_QUEUE_KEY) || '[]'); } catch { return []; }
}

function saveSyncQueue(queue) {
  try { localStorage.setItem(SYNC_QUEUE_KEY, JSON.stringify(queue)); } catch {}
}

function addToQueue(operation) {
  const queue = getSyncQueue();
  queue.push({ ...operation, queuedAt: new Date().toISOString() });
  saveSyncQueue(queue);
}

// ─── Check if we're online and Supabase is available ─────────────────────────
function canSync() {
  return isSupabaseEnabled() && navigator.onLine;
}

// ─── Get current Supabase user ID ────────────────────────────────────────────
async function getUserId() {
  if (!supabase) return null;
  const { data: { user } } = await supabase.auth.getUser();
  return user?.id || null;
}

// ═══════════════════════════════════════════════════════════════════════════════
// PUSH — Send local data to Supabase
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Push a single certificate to Supabase
 */
export async function pushCertificate(cert) {
  if (!canSync()) {
    addToQueue({ type: 'upsert', table: 'certificates', data: cert });
    return;
  }
  try {
    const userId = await getUserId();
    if (!userId) return;

    const row = {
      user_id: userId,
      cert_type: cert.certType || cert.type || 'gsc',
      file_ref: cert.fileRef || cert.fileReference || null,
      data: cert,
      saved_at: cert.savedAt || new Date().toISOString(),
      synced_from: getDeviceId(),
    };

    // Use local_id for dedup — if cert has an id, upsert by matching data->id
    const { error } = await supabase
      .from('certificates')
      .upsert(row, { onConflict: 'id' });

    if (error) console.warn('[Sync] Push cert error:', error.message);
  } catch (e) {
    console.warn('[Sync] Push cert failed:', e.message);
    addToQueue({ type: 'upsert', table: 'certificates', data: cert });
  }
}

/**
 * Push all records of a type (batch sync)
 */
export async function pushAll(table, items) {
  if (!canSync()) {
    addToQueue({ type: 'batch', table, count: items.length });
    return;
  }
  try {
    const userId = await getUserId();
    if (!userId) return;

    const rows = items.map(item => ({
      user_id: userId,
      data: item,
      saved_at: item.savedAt || item.createdAt || new Date().toISOString(),
    }));

    // Delete existing and re-insert (full sync for simplicity)
    await supabase.from(table).delete().eq('user_id', userId);
    if (rows.length > 0) {
      const { error } = await supabase.from(table).insert(rows);
      if (error) console.warn(`[Sync] Push ${table} error:`, error.message);
    }
  } catch (e) {
    console.warn(`[Sync] Push ${table} failed:`, e.message);
  }
}

/**
 * Push profile to Supabase
 */
export async function pushProfile(profile) {
  if (!canSync()) {
    addToQueue({ type: 'upsert', table: 'profiles', data: profile });
    return;
  }
  try {
    const userId = await getUserId();
    if (!userId) return;

    const row = {
      user_id: userId,
      username: profile.username || 'default',
      display_name: profile.displayName || profile.engineerName || null,
      company_name: profile.companyName || null,
      company_type: profile.companyType || null,
      company_number: profile.companyNumber || null,
      vat_reg_number: profile.vatRegNumber || null,
      company_addr: profile.companyAddr || null,
      company_postcode: profile.companyPostcode || null,
      company_tel: profile.companyTel || null,
      company_email: profile.companyEmail || null,
      company_web: profile.companyWeb || null,
      gas_safe_no: profile.gasSafeNo || null,
      engineer_name: profile.engineerName || null,
      gas_id: profile.gasId || null,
      plan: profile.plan || 'lite',
    };

    const { error } = await supabase
      .from('profiles')
      .upsert(row, { onConflict: 'user_id' });

    if (error) console.warn('[Sync] Push profile error:', error.message);
  } catch (e) {
    console.warn('[Sync] Push profile failed:', e.message);
  }
}

/**
 * Push contacts to Supabase
 */
export async function pushContacts(contacts) {
  if (!canSync()) {
    addToQueue({ type: 'batch', table: 'contacts', count: contacts.length });
    return;
  }
  try {
    const userId = await getUserId();
    if (!userId) return;

    // Full replace
    await supabase.from('contacts').delete().eq('user_id', userId);
    if (contacts.length > 0) {
      const rows = contacts.map(c => ({
        user_id: userId,
        name: c.name || c.displayName || null,
        company: c.company || null,
        email: c.email || null,
        phone: c.phone || c.tel || null,
        address: c.address || null,
        postcode: c.postcode || null,
        notes: c.notes || null,
        data: c,
      }));
      const { error } = await supabase.from('contacts').insert(rows);
      if (error) console.warn('[Sync] Push contacts error:', error.message);
    }
  } catch (e) {
    console.warn('[Sync] Push contacts failed:', e.message);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// PULL — Fetch cloud data and merge with local
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Pull all data from Supabase for the current user
 * Returns { records, invoices, quotes, contacts, accountReports, gscFolders, profile }
 */
export async function pullAll() {
  if (!canSync()) return null;

  try {
    const userId = await getUserId();
    if (!userId) return null;

    const [
      { data: certs },
      { data: invs },
      { data: qts },
      { data: cts },
      { data: rpts },
      { data: fldrs },
      { data: prof },
    ] = await Promise.all([
      supabase.from('certificates').select('*').eq('user_id', userId).order('saved_at', { ascending: false }),
      supabase.from('invoices').select('*').eq('user_id', userId).order('saved_at', { ascending: false }),
      supabase.from('quotes').select('*').eq('user_id', userId).order('saved_at', { ascending: false }),
      supabase.from('contacts').select('*').eq('user_id', userId),
      supabase.from('account_reports').select('*').eq('user_id', userId),
      supabase.from('gsc_folders').select('*').eq('user_id', userId),
      supabase.from('profiles').select('*').eq('user_id', userId).single(),
    ]);

    return {
      records: (certs || []).map(c => c.data),
      invoices: (invs || []).map(i => i.data),
      quotes: (qts || []).map(q => q.data),
      contacts: (cts || []).map(c => c.data),
      accountReports: (rpts || []).map(r => r.data),
      gscFolders: (fldrs || []).map(f => f.data),
      profile: prof || null,
    };
  } catch (e) {
    console.warn('[Sync] Pull failed:', e.message);
    return null;
  }
}

/**
 * Merge cloud data with local data (cloud wins for conflicts, union for new items)
 * Uses savedAt timestamp as tiebreaker
 */
export function mergeRecords(local, cloud) {
  if (!cloud || !cloud.length) return local;
  if (!local || !local.length) return cloud;

  // Build a map by a unique key (fileRef + savedAt combo, or just savedAt)
  const merged = new Map();

  // Local first
  local.forEach(r => {
    const key = r.fileRef || r.savedAt || JSON.stringify(r).slice(0, 100);
    merged.set(key, r);
  });

  // Cloud overwrites if newer
  cloud.forEach(r => {
    const key = r.fileRef || r.savedAt || JSON.stringify(r).slice(0, 100);
    const existing = merged.get(key);
    if (!existing) {
      merged.set(key, r);
    } else if (r.savedAt && existing.savedAt && new Date(r.savedAt) > new Date(existing.savedAt)) {
      merged.set(key, r);
    }
  });

  return Array.from(merged.values());
}

// ═══════════════════════════════════════════════════════════════════════════════
// FLUSH QUEUE — Process offline writes when back online
// ═══════════════════════════════════════════════════════════════════════════════
export async function flushSyncQueue() {
  if (!canSync()) return;

  const queue = getSyncQueue();
  if (!queue.length) return;

  console.log(`[Sync] Flushing ${queue.length} queued operations...`);
  const failed = [];

  for (const op of queue) {
    try {
      if (op.table === 'profiles') {
        await pushProfile(op.data);
      } else if (op.table === 'certificates') {
        await pushCertificate(op.data);
      } else if (op.table === 'contacts') {
        await pushContacts(op.data);
      }
    } catch {
      failed.push(op);
    }
  }

  saveSyncQueue(failed);
  if (failed.length) {
    console.warn(`[Sync] ${failed.length} operations still queued`);
  } else {
    console.log('[Sync] Queue flushed successfully');
  }
}

// ─── Device ID (for conflict resolution) ─────────────────────────────────────
function getDeviceId() {
  let id = localStorage.getItem('wlg_device_id');
  if (!id) {
    id = 'dev_' + Math.random().toString(36).slice(2, 10);
    localStorage.setItem('wlg_device_id', id);
  }
  return id;
}

// ─── Listen for online/offline events ────────────────────────────────────────
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    console.log('[Sync] Back online — flushing queue...');
    flushSyncQueue();
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// AUTH HELPERS
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * Sign up a new user with email/password
 */
export async function signUp(email, password, metadata = {}) {
  if (!supabase) throw new Error('Supabase not configured');
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: metadata },
  });
  if (error) throw error;
  return data;
}

/**
 * Sign in with email/password
 */
export async function signIn(email, password) {
  if (!supabase) throw new Error('Supabase not configured');
  const { data, error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
  return data;
}

/**
 * Reset password — sends a password reset email via Supabase
 */
export async function resetPassword(email) {
  if (!supabase) throw new Error('Supabase not configured');
  const { data, error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: window.location.origin + '/#reset-password',
  });
  if (error) throw error;
  return data;
}

/**
 * Update password — used after clicking the reset link
 */
export async function updatePassword(newPassword) {
  if (!supabase) throw new Error('Supabase not configured');
  const { data, error } = await supabase.auth.updateUser({ password: newPassword });
  if (error) throw error;
  return data;
}

/**
 * Look up username (email) by Gas Safe number or engineer name
 */
export async function lookupUsername(gasSafeNo, engineerName) {
  if (!supabase) throw new Error('Supabase not configured');
  let query = supabase.from('profiles').select('username, engineer_name, gas_safe_no');
  if (gasSafeNo && gasSafeNo.trim()) {
    query = query.eq('gas_safe_no', gasSafeNo.trim());
  } else if (engineerName && engineerName.trim()) {
    query = query.ilike('engineer_name', `%${engineerName.trim()}%`);
  } else {
    throw new Error('Please provide your Gas Safe number or engineer name.');
  }
  const { data, error } = await query;
  if (error) throw error;
  return data || [];
}

/**
 * Sign out
 */
export async function signOut() {
  if (!supabase) return;
  await supabase.auth.signOut();
}

/**
 * Get current session
 */
export async function getSession() {
  if (!supabase) return null;
  const { data: { session } } = await supabase.auth.getSession();
  return session;
}

/**
 * Listen for auth state changes
 */
export function onAuthStateChange(callback) {
  if (!supabase) return { data: { subscription: { unsubscribe: () => {} } } };
  return supabase.auth.onAuthStateChange(callback);
}
