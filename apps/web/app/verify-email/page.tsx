"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

import { apiFetch } from "@/lib/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Missing verification token.");
      return;
    }
    apiFetch<{ message: string }>("/api/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    })
      .then((res) => {
        setStatus("success");
        setMessage(res.message || "Email verified. You can sign in.");
      })
      .catch(() => {
        setStatus("error");
        setMessage("Invalid or expired verification link.");
      });
  }, [token]);

  if (status === "loading") {
    return (
      <Card className="w-full max-w-sm">
        <CardHeader>
          <CardTitle>Verifying your email</CardTitle>
          <CardDescription>Please wait…</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse text-sm text-muted-foreground">
            Checking your link…
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-sm">
      <CardHeader>
        <CardTitle>
          {status === "success" ? "Email verified" : "Verification failed"}
        </CardTitle>
        <CardDescription>{message}</CardDescription>
      </CardHeader>
      <CardFooter className="flex flex-col gap-2">
        {status === "success" ? (
          <Button className="w-full" onClick={() => router.push("/login")}>
            Sign in
          </Button>
        ) : (
          <Button variant="outline" asChild className="w-full">
            <Link href="/register">Create an account</Link>
          </Button>
        )}
        <Button variant="ghost" asChild className="w-full">
          <Link href="/">Back to home</Link>
        </Button>
      </CardFooter>
    </Card>
  );
}

export default function VerifyEmailPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-background text-foreground px-4">
      <Suspense
        fallback={
          <Card className="w-full max-w-sm">
            <CardHeader>
              <CardTitle>Verifying your email</CardTitle>
              <CardDescription>Please wait…</CardDescription>
            </CardHeader>
          </Card>
        }
      >
        <VerifyEmailContent />
      </Suspense>
    </main>
  );
}
