// ═══════════════════════════════════════════════════════════════════════════════
// Supabase Client — Gas Safe App
// ═══════════════════════════════════════════════════════════════════════════════
import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Only create client if env vars are set (allows app to work without Supabase during dev)
export const supabase = (SUPABASE_URL && SUPABASE_ANON_KEY)
  ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
        storageKey: 'wlg_supabase_auth',
      },
    })
  : null;

export const isSupabaseEnabled = () => !!supabase;
