# Supabase Setup Guide — Gas Safe App

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up / log in
2. Click **"New Project"**
3. Fill in:
   - **Name**: `gas-safe-app`
   - **Database Password**: (save this somewhere safe)
   - **Region**: `eu-west-2` (London) — closest to your users
4. Click **"Create new project"** — wait ~2 minutes for provisioning

## Step 2: Run the Database Migration

1. In Supabase Dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Copy-paste the entire contents of `supabase/migrations/001_initial_schema.sql`
4. Click **"Run"** — should say "Success. No rows returned"

## Step 3: Get Your API Keys

1. Go to **Settings** → **API** (left sidebar)
2. Copy these values:
   - **Project URL** (looks like `https://xxxx.supabase.co`)
   - **anon / public** key (safe for client-side)
   - **service_role** key (server-side only — NEVER expose to client)

## Step 4: Add Environment Variables to Netlify

Go to Netlify Dashboard → Site settings → Environment variables. Add:

| Variable | Value | Where Used |
|----------|-------|------------|
| `VITE_SUPABASE_URL` | Your Project URL | Client-side (React app) |
| `VITE_SUPABASE_ANON_KEY` | Your anon/public key | Client-side (React app) |
| `SUPABASE_URL` | Your Project URL | Server-side (Netlify Functions) |
| `SUPABASE_SERVICE_KEY` | Your service_role key | Server-side (Netlify Functions) |

**Important**: `VITE_` prefix makes the var available to the Vite build (client-side).
The non-VITE ones are only available in Netlify Functions (server-side).

## Step 5: Enable Email Auth in Supabase

1. Go to **Authentication** → **Providers** (left sidebar)
2. **Email** should be enabled by default
3. Under **Authentication** → **Settings**:
   - Set **Site URL** to `https://gas-safety-app.com`
   - Add `https://gas-safety-app.com` to **Redirect URLs**

## Step 6: Redeploy

Push to GitHub or trigger a manual deploy in Netlify to pick up the new env vars.

## Architecture

```
┌─────────────────────────┐
│   React PWA (Browser)   │
│                         │
│  localStorage (offline) │◄────── Always works, even offline
│         │               │
│  syncEngine.js          │──────► Supabase (cloud backup)
│         │               │        - PostgreSQL database
│  supabaseClient.js      │        - Row-Level Security
└─────────────────────────┘        - Auth (email/password)
         │
         ▼
┌─────────────────────────┐
│  Netlify Functions      │
│                         │
│  stripe-webhook.js      │──────► Stripe (payments)
│  check-subscription.js  │──────► Supabase (plan updates)
└─────────────────────────┘
```

**Offline-first**: localStorage remains the primary store. Supabase syncs in the background when online. If offline, writes queue up and flush when connectivity returns.
