# TokenToast

**A production-ready authentication API and web app.** Secure sign-up, login, email verification, password reset, and session management—built with FastAPI, Next.js, and modern tooling.

---

## Why this project exists

I built **TokenToast** to **learn FastAPI deeply** and to practice **better system design**. Authentication is one of those domains where every choice—where you store tokens, how you rotate them, how you rate-limit and log—has real security and scalability consequences. So instead of gluing together half-understood snippets, I wanted a single, coherent project that:

- **Teaches FastAPI** — Dependency injection, async request handling, Pydantic schemas, structured routing, and how a real API is organized.
- **Forces clear boundaries** — Routes → services → models; no business logic in endpoints, no SQL in handlers. Each layer has a job.
- **Surfaces system-design tradeoffs** — Why HTTP-only cookies instead of `localStorage`? Why store refresh tokens in the DB? Why rate-limit at the gateway/app layer? Why log refresh-token reuse? The code reflects those decisions.
- **Stays deployable** — Env-based config, migrations (Alembic), optional SMTP, fail-open rate limiting when Redis is down. So it’s not just a tutorial: it’s a reference for “how I’d do auth in a small production service.”

If you’re learning FastAPI or thinking through auth and session design, this repo is a detailed example you can read and extend.

---

## What it is

TokenToast is a **full-stack auth platform** in a **Turborepo monorepo**:

| Part | Stack | Role |
|------|--------|------|
| **API** | FastAPI (Python) | Auth routes, JWT issuance, cookie handling, rate limiting, email (SMTP), session listing/revocation. |
| **Web** | Next.js 16 (React 19) | Landing page, login/register/dashboard, forgot/reset/verify-email flows, protected routes, session UI. |

The backend exposes a REST-style auth API; the frontend talks to it with `fetch` and credentials (cookies). No magic SDKs—just clear contracts and a single source of truth for sessions and users.

---

## Features

### Core auth

- **Registration** — Email + password, Argon2 hashing, JWT access + refresh tokens in HTTP-only cookies. Optional verification email on sign-up.
- **Login** — Email/password validation, cookie-based session. Redirect support (e.g. after “forgot password”).
- **Logout** — Clears auth cookies and revokes the current refresh token in the database.
- **Refresh** — Silent token refresh; short-lived access tokens, longer-lived refresh tokens with rotation.
- **Current user** — `GET /api/auth/me` returns the authenticated user (id, email, is_verified, role).

### Email flows

- **Email verification** — Sign-up sends a time-limited, one-time link (SMTP or console in dev). `POST /api/auth/verify-email` marks the user verified.
- **Resend verification** — By email; same “don’t leak account existence” behavior.
- **Forgot password** — Submit email; time-limited reset link sent (or logged). Rate limited per IP.
- **Reset password** — Token in link; one-time use, then invalidated.

### Session management

- **List sessions** — `GET /api/auth/sessions` returns active refresh tokens (id, created_at, expires_at, `is_current`).
- **Revoke a session** — `DELETE /api/auth/sessions/{session_id}` revokes one device/session.
- **Refresh-token reuse detection** — If a refresh token is reused after rotation, all sessions for that user are revoked and a security event is logged (e.g. for SIEM/monitoring).

### Security and reliability

- **Rate limiting** — Redis-backed limits on login, registration, and forgot-password (per IP). Fail-open if Redis is unavailable.
- **CORS** — Single allowed origin (`FRONTEND_ORIGIN`) with credentials.
- **Cookies** — HttpOnly, configurable Secure and SameSite for production (HTTPS).
- **Security logging** — Structured log for refresh-token reuse; ready to plug into monitoring.

### Role-based access

- **Admin** — Example protected route: `GET /api/auth/admin/ping` and `/admin` require the `admin` role.

---

## Tech stack

| Layer | Technologies |
|-------|----------------|
| **API** | FastAPI, Uvicorn, Pydantic, SQLAlchemy (async), asyncpg, Redis, Argon2, PyJWT, Alembic |
| **Web** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui, Zustand, react-hook-form, zod, Hugeicons |
| **Monorepo** | Turborepo, pnpm |

---

## Architecture and system design

### High-level flow

```
┌─────────────┐     HTTPS      ┌─────────────┐     TCP      ┌──────────────┐
│   Browser   │ ◄────────────► │  Next.js    │ ◄──────────► │   FastAPI    │
│  (cookies)  │   credentials  │  (proxy /   │   API calls  │   (auth +    │
│             │                │   SPA)      │   + cookies  │   sessions)  │
└─────────────┘                └─────────────┘              └──────┬───────┘
                                                                   │
                    ┌──────────────────────────────────────────────┼────────────────────────────────┐
                    │                                              │                                │
                    ▼                                              ▼                                ▼
             ┌─────────────┐                                 ┌─────────────┐                  ┌─────────────┐
             │ PostgreSQL │                                 │   Redis     │                  │  SMTP       │
             │ users,     │                                 │ rate limits │                  │  (optional) │
             │ refresh_   │                                 │ (optional)  │                  │  emails     │
             │ tokens,    │                                 └─────────────┘                  └─────────────┘
             │ email_     │
             │ tokens     │
             └─────────────┘
```

### Design decisions (and why)

- **HTTP-only cookies for tokens** — Access and refresh tokens are set by the API and sent automatically by the browser. Scripts cannot read them, which reduces XSS risk compared to `localStorage`.
- **Refresh tokens in the database** — Each refresh token is stored (hashed) with an expiry and a `revoked` flag. Logout and “revoke session” simply flip the flag; reuse detection revokes all tokens for the user.
- **One-time refresh tokens** — After issuing a new refresh token, the old one is revoked. If the old one is used again, we treat it as reuse and revoke every session for that user, then log a security event.
- **Rate limiting in the app** — Login, register, and forgot-password are rate limited per IP using Redis. If Redis is down, we skip limiting (fail-open) so the app still works in dev or degraded environments.
- **Separate email tokens** — Verification and reset use their own table: hashed token, type, expiry, one-time use. No reuse of the same token for different flows.
- **Layered API** — Routes only validate input and call services; services contain business logic and use repositories (SQLAlchemy models). Clear separation makes testing and evolution easier.

---

## Project structure

```
tokentoast/
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── app/
│   │   │   ├── core/                 # Config, DB, Redis, security, security_log
│   │   │   ├── dependencies/         # get_current_user, require_roles
│   │   │   ├── models/               # User, RefreshToken, EmailToken
│   │   │   ├── routes/               # auth (register, login, sessions, etc.)
│   │   │   ├── schemas/              # Pydantic request/response models
│   │   │   ├── services/             # auth_service, verification_service, email_service
│   │   │   └── utils/                # cookies, rate_limit
│   │   ├── alembic/                  # Migrations
│   │   ├── tests/                    # pytest (e.g. test_auth.py)
│   │   ├── main.py
│   │   └── requirements.txt
│   │
│   └── web/                          # Next.js frontend
│       ├── app/
│       │   ├── auth/                 # AuthBootstrap (init /me on load)
│       │   ├── login/, register/, dashboard/, admin/
│       │   ├── forgot-password/, reset-password/, verify-email/
│       │   ├── layout.tsx
│       │   └── page.tsx              # Landing
│       ├── components/
│       ├── lib/                      # api.ts (apiFetch)
│       ├── store/                    # auth-store (Zustand)
│       └── middleware.ts            # Public vs protected routes
│
├── package.json                      # Turborepo scripts
├── turbo.json
└── pnpm-workspace.yaml
```

---

## Getting started

### Prerequisites

- **Node.js** 18+ and **pnpm**
- **Python** 3.11+ and **venv** (or similar)
- **PostgreSQL** (e.g. local or Docker)
- **Redis** (optional; used for rate limiting; app works without it in dev)

### 1. Clone and install

```bash
git clone https://github.com/your-username/tokentoast.git
cd tokentoast
pnpm install
```

### 2. API setup

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Copy the example env and set at least `DATABASE_URL` (and optionally SMTP and Redis):

```bash
cp .env.example .env
# Edit .env: DATABASE_URL, REDIS_URL, and optionally SMTP_* for email
```

Run migrations:

```bash
alembic upgrade head
```

### 3. Web env

In `apps/web`, create `.env.local` if you need to point at a different API:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

(Defaults to `http://localhost:8000` if unset.)

### 4. Run everything

From the **repo root**:

```bash
pnpm dev
```

This starts:

- **API** — http://localhost:8000 (Uvicorn)
- **Web** — http://localhost:3000 (Next.js)

Open http://localhost:3000 and use “Get started” / “Create account” to run through the flows.

### 5. Run API tests

```bash
cd apps/api
# Ensure DB is up and migrated: alembic upgrade head
pytest
```

---

## API overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register; returns user, sets cookies. Sends verification email if SMTP configured. |
| `POST` | `/api/auth/login` | Login; returns tokens, sets cookies. |
| `POST` | `/api/auth/logout` | Logout; revokes current refresh token, clears cookies. |
| `GET`  | `/api/auth/me` | Current user (requires auth). |
| `POST` | `/api/auth/refresh` | Issue new access + refresh token; revokes previous refresh token. |
| `GET`  | `/api/auth/sessions` | List active sessions (requires auth). |
| `DELETE` | `/api/auth/sessions/{session_id}` | Revoke one session (requires auth). |
| `POST` | `/api/auth/verify-email` | Verify email with token from link. |
| `POST` | `/api/auth/resend-verification` | Resend verification email (body: `email`). |
| `POST` | `/api/auth/forgot-password` | Send reset link (body: `email`); rate limited. |
| `POST` | `/api/auth/reset-password` | Set new password (body: `token`, `new_password`). |
| `GET`  | `/api/auth/admin/ping` | Example admin-only route. |

OpenAPI docs (when the API is running): **http://localhost:8000/docs**.

---

## Environment variables (API)

Example and meaning (see `apps/api/.env.example` for a full template):

| Variable | Purpose |
|----------|---------|
| `ENVIRONMENT` | `development` \| `staging` \| `production` |
| `DATABASE_URL` | PostgreSQL connection string (async). |
| `JWT_SECRET_KEY` | Secret for signing JWTs (use a long, random value in production). |
| `COOKIE_SECURE`, `COOKIE_SAMESITE` | Cookie flags (e.g. `true` / `Strict` in production). |
| `REDIS_URL` | Redis URL for rate limiting (optional). |
| `FRONTEND_ORIGIN` | Allowed CORS origin and base URL for links in emails. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME` | SMTP for verification and reset emails; leave `SMTP_HOST` empty to only log links in dev. |

---

## What you can learn from this project

- **FastAPI** — Dependency injection (`Depends`), async handlers, Pydantic request/response models, and organizing a real API.
- **Auth design** — Cookie-based sessions, refresh rotation, reuse detection, and why we store and revoke refresh tokens.
- **Layered design** — Routes → services → data; clear responsibilities and testability.
- **Operational concerns** — Config via env, migrations (Alembic), rate limiting with fail-open, and security logging.
- **Full-stack integration** — How a Next.js app calls an external API with credentials and handles 401/refresh.

Use it as a reference, extend it (e.g. OAuth, MFA, sessions UI on the dashboard), or strip it down to the parts you care about.

---

## License

ISC.
