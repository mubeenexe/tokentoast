import Link from "next/link";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { HugeiconsIcon } from "@hugeicons/react";
import {
  ShieldIcon,
  MailIcon,
  UserIcon,
  DatabaseIcon,
  Tick02Icon,
  RefreshIcon,
  LogoutIcon,
  KeyIcon,
  ComputerIcon,
  LayoutIcon,
} from "@hugeicons/core-free-icons";

export default function Page() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero */}
      <header className="border-b border-border/50 bg-card/30">
        <div className="container mx-auto flex max-w-5xl flex-col items-center gap-8 px-6 py-16 text-center md:py-24">
          <Badge variant="secondary" className="text-xs">
            Authentication & Sessions
          </Badge>
          <h1 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl lg:text-6xl">
            TokenToast
          </h1>
          <p className="max-w-2xl text-lg text-muted-foreground md:text-xl">
            A production-ready authentication API and web app. Secure sign-up, login, email
            verification, password reset, and session management—built with FastAPI, Next.js,
            and modern tooling.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Button asChild size="lg">
              <Link href="/login">Get started</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/register">Create account</Link>
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto max-w-5xl px-6 py-16">
        {/* What is TokenToast */}
        <section className="mb-20">
          <h2 className="mb-4 text-2xl font-semibold text-foreground">
            What is TokenToast?
          </h2>
          <p className="max-w-3xl text-muted-foreground leading-relaxed">
            TokenToast is a full-stack authentication platform that gives you a complete
            auth flow out of the box: user registration, login, logout, email verification,
            forgot password, and reset password. The backend is a FastAPI service with JWT
            access and refresh tokens, HTTP-only cookies, and Redis-backed rate limiting and
            session storage. The frontend is a Next.js app that consumes the API and
            provides a polished, responsive UI. Whether you&apos;re building a SaaS, internal
            tool, or side project, TokenToast lets you focus on your product instead of
            reinventing auth.
          </p>
        </section>

        <Separator className="my-12" />

        {/* Features */}
        <section className="mb-20">
          <h2 className="mb-2 text-2xl font-semibold text-foreground">Features</h2>
          <p className="mb-10 text-muted-foreground">
            Everything you need for secure, scalable authentication.
          </p>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <HugeiconsIcon icon={UserIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle>Register & Login</CardTitle>
                <CardDescription>
                  Email/password registration and login with validation. Passwords are
                  hashed securely; JWT access and refresh tokens are issued and stored in
                  HTTP-only cookies.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <HugeiconsIcon icon={MailIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle>Email Verification</CardTitle>
                <CardDescription>
                  Optional email verification on sign-up. Verification links are sent via
                  configurable SMTP; in development, links can be logged instead of sent.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <HugeiconsIcon icon={KeyIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle>Forgot & Reset Password</CardTitle>
                <CardDescription>
                  Forgot-password flow with time-limited reset links sent by email. Reset
                  tokens are validated and invalidated after use.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <HugeiconsIcon icon={RefreshIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle>Session Management</CardTitle>
                <CardDescription>
                  List active sessions and revoke individual refresh tokens. Users can see
                  where they&apos;re logged in and sign out from specific devices.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <HugeiconsIcon icon={LogoutIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle>Logout & Token Refresh</CardTitle>
                <CardDescription>
                  Logout clears cookies and invalidates the refresh token. Silent token
                  refresh keeps users signed in without re-entering credentials.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <HugeiconsIcon icon={ShieldIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle>Rate Limiting</CardTitle>
                <CardDescription>
                  Redis-backed rate limits on login, registration, and forgot-password to
                  reduce abuse and brute-force attempts. Limits are configurable per
                  environment.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </section>

        <Separator className="my-12" />

        {/* Why TokenToast */}
        <section className="mb-20">
          <h2 className="mb-2 text-2xl font-semibold text-foreground">
            Why TokenToast?
          </h2>
          <p className="mb-10 text-muted-foreground">
            Built for reliability, security, and developer experience.
          </p>
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HugeiconsIcon icon={Tick02Icon} className="size-5 text-primary" strokeWidth={2} />
                  Production-ready
                </CardTitle>
                <CardDescription>
                  Async PostgreSQL (asyncpg), Redis for rate limiting and session data,
                  configurable CORS and cookie settings, and environment-based configuration
                  so you can run the same code in dev, staging, and production.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HugeiconsIcon icon={Tick02Icon} className="size-5 text-primary" strokeWidth={2} />
                  Secure by default
                </CardTitle>
                <CardDescription>
                  JWT with short-lived access tokens and refresh token rotation, HTTP-only
                  cookies to mitigate XSS, optional email verification, and hashed
                  passwords. Rate limiting adds an extra layer against brute force and
                  abuse.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HugeiconsIcon icon={Tick02Icon} className="size-5 text-primary" strokeWidth={2} />
                  Modern stack
                </CardTitle>
                <CardDescription>
                  FastAPI on the backend for performance and automatic OpenAPI docs;
                  Next.js on the frontend with App Router and server components. Monorepo
                  with Turbo and pnpm for a single place to develop and deploy.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HugeiconsIcon icon={Tick02Icon} className="size-5 text-primary" strokeWidth={2} />
                  Easy to extend
                </CardTitle>
                <CardDescription>
                  Clear separation between routes, services, and models. Alembic
                  migrations for schema changes, dependency injection for testing, and
                  optional admin endpoints. Add roles, OAuth, or MFA on top of the existing
                  foundation.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </section>

        <Separator className="my-12" />

        {/* Tech stack */}
        <section className="mb-20">
          <h2 className="mb-2 text-2xl font-semibold text-foreground">Tech stack</h2>
          <p className="mb-10 text-muted-foreground">
            Backend, frontend, and infrastructure.
          </p>
          <div className="flex flex-wrap gap-3">
            <Badge variant="secondary">FastAPI</Badge>
            <Badge variant="secondary">Next.js 16</Badge>
            <Badge variant="secondary">PostgreSQL</Badge>
            <Badge variant="secondary">Redis</Badge>
            <Badge variant="secondary">JWT</Badge>
            <Badge variant="secondary">Alembic</Badge>
            <Badge variant="secondary">SQLAlchemy (async)</Badge>
            <Badge variant="secondary">Pydantic</Badge>
            <Badge variant="secondary">React 19</Badge>
            <Badge variant="secondary">TypeScript</Badge>
            <Badge variant="secondary">Tailwind CSS</Badge>
            <Badge variant="secondary">shadcn/ui</Badge>
            <Badge variant="secondary">Turbo</Badge>
            <Badge variant="secondary">pnpm</Badge>
            <Badge variant="secondary">Docker</Badge>
          </div>
          <div className="mt-10 grid gap-6 sm:grid-cols-3">
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                  <HugeiconsIcon icon={ComputerIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle className="text-base">API</CardTitle>
                <CardDescription>
                  FastAPI app with auth routes, cookie handling, rate limiting, and
                  optional email (SMTP). Runs with Uvicorn; database and Redis configured
                  via env.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                  <HugeiconsIcon icon={DatabaseIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle className="text-base">Data</CardTitle>
                <CardDescription>
                  PostgreSQL for users and refresh tokens; Redis for rate limits and
                  revocation. Docker Compose included for local Postgres and Redis.
                </CardDescription>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader>
                <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                  <HugeiconsIcon icon={LayoutIcon} className="size-5" strokeWidth={2} />
                </div>
                <CardTitle className="text-base">Web app</CardTitle>
                <CardDescription>
                  Next.js with App Router, middleware for auth, and a UI built with
                  shadcn components. Connects to the API via fetch with credentials for
                  cookies.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </section>

        {/* CTA */}
        <section className="rounded-2xl border border-border bg-card p-8 text-center md:p-12">
          <h2 className="mb-2 text-xl font-semibold text-foreground md:text-2xl">
            Ready to use TokenToast?
          </h2>
          <p className="mb-6 text-muted-foreground">
            Sign up or log in to try the full auth flow and session management.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Button asChild size="lg">
              <Link href="/register">Create account</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/login">Sign in</Link>
            </Button>
          </div>
        </section>
      </main>

      <footer className="border-t border-border/50 py-8">
        <div className="container mx-auto max-w-5xl px-6 text-center text-sm text-muted-foreground">
          TokenToast — Authentication API &amp; Web App. Built with FastAPI, Next.js, and
          modern tooling.
        </div>
      </footer>
    </div>
  );
}
