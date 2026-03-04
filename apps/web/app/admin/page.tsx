"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useShallow } from "zustand/react/shallow";

import { useAuthStore } from "@/store/auth-store";
import { apiFetch } from "@/lib/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";

type AdminPing = {
  message: string;
  user_id: string;
};

export default function AdminPage() {
  const router = useRouter();
  const { user, loading } = useAuthStore(
    useShallow((s) => ({
      user: s.user,
      loading: s.loading,
    }))
  );
  const [ping, setPing] = useState<AdminPing | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.replace("/login");
      } else if (user.role !== "admin") {
        router.replace("/dashboard");
      }
    }
  }, [loading, user, router]);

  useEffect(() => {
    if (!user || user.role !== "admin") return;
    void (async () => {
      try {
        const data = await apiFetch<AdminPing>("/api/auth/admin/ping");
        setPing(data);
      } catch (err: any) {
        setError(err?.message ?? "Failed to reach admin API");
      }
    })();
  }, [user]);

  if (loading || (!user && typeof window !== "undefined")) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <div>Loading...</div>
      </main>
    );
  }

  if (!user || user.role !== "admin") {
    return null;
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background text-foreground px-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Admin Panel</CardTitle>
          <CardDescription>Admin-only operations for TokenToast.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {error && <p className="text-destructive text-xs">{error}</p>}
          {ping ? (
            <p className="text-muted-foreground">
              {ping.message} (user_id: {ping.user_id})
            </p>
          ) : (
            <p className="text-muted-foreground">Checking admin access…</p>
          )}
        </CardContent>
      </Card>
    </main>
  );
}

