# Authentication SOP (Standard Operating Procedure)

## Architecture Overview

Supabase Auth with Google OAuth on Next.js (deployed on Vercel).

## Auth Flow

1. User clicks "Se connecter" → `AuthModal` opens
2. User clicks "Continuer avec Google" → `signInWithOAuth({ provider: 'google' })`
3. Google redirects to Supabase → `https://<project>.supabase.co/auth/v1/callback`
4. Supabase redirects to app → `/auth/callback` (with code)
5. App exchanges code for session → `exchangeCodeForSession(code)`
6. App redirects to `/` with valid cookies

## Critical Components

- **`src/middleware.ts`** — Refreshes auth token on EVERY request. Without this, sessions expire and RLS queries silently return empty data.
- **`src/lib/supabase.ts`** — Browser client (singleton via `createBrowserClient`).
- **`src/lib/supabase-server.ts`** — Server client (uses cookies from Next.js `headers`).
- **`src/app/auth/callback/route.ts`** — Server Route handler that exchanges OAuth code for session.
- **`src/components/auth/auth-modal.tsx`** — Login UI (Google OAuth + Magic Link).
- **`src/components/auth/user-menu.tsx`** — Displays user info or login button.

## Lessons Learned

1. **Middleware is MANDATORY** for Supabase Auth in Next.js. Without it, auth cookies are never refreshed, causing silent failures on other devices/tabs.
2. **Use `getUser()` not `getSession()`** — `getUser()` validates the token server-side. `getSession()` only reads the local cookie and can return stale/invalid data.
3. **Vercel Environment Variables** — `.env.local` is NOT deployed. Keys must be added manually in Vercel Settings > Environment Variables for Production, Preview, AND Development.
4. **Redirect URLs in Supabase Dashboard** — Must include the production URL with wildcard: `https://archihub-gamma.vercel.app/**` AND preview URLs: `https://*-fogwoungsarahlaure-8851s-projects.vercel.app/**`.
5. **Google Cloud Console** — The authorized redirect URI must point to Supabase: `https://ifrtjbbrickwjfexqskm.supabase.co/auth/v1/callback`.
6. **Publishable Key** — The project uses `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY` (format: `sb_publishable_...`), not the legacy `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
7. **Stabilize Supabase client in React** — Use `useRef(createClient())` to avoid unnecessary re-renders from dependency arrays.

## RLS Policies (saved_articles)

- SELECT: `auth.uid() = user_id`
- INSERT: `auth.uid() = user_id`
- DELETE: `auth.uid() = user_id`
