"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useShallow } from "zustand/react/shallow";

import { useAuthStore } from "@/store/auth-store";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading, logout } = useAuthStore(
    useShallow((s) => ({
      user: s.user,
      loading: s.loading,
      logout: s.logout,
    }))
  );

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading || (!user && typeof window !== "undefined")) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-background text-foreground">
        <div>Loading...</div>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-background text-foreground px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Dashboard</CardTitle>
            <CardDescription>Welcome back to TokenToast.</CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => logout().then(() => router.replace("/login"))}
          >
            Sign out
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="text-sm">
            <div className="text-xs text-muted-foreground">Signed in as</div>
            <div className="font-mono text-sm">{user.email}</div>
          </div>
          <div className="flex gap-4 text-xs text-muted-foreground">
            <div>
              <div className="text-[0.7rem] uppercase tracking-wide">
                Role
              </div>
              <div className="font-medium">{user.role}</div>
            </div>
            <div>
              <div className="text-[0.7rem] uppercase tracking-wide">
                Verified
              </div>
              <div className="font-medium">
                {user.is_verified ? "Yes" : "No"}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </main>
  );
}

