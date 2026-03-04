"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import LoginForm from "./LoginForm";

function LoginContent() {
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/dashboard";
  return <LoginForm redirectTo={redirectTo} />;
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginForm redirectTo="/dashboard" />}>
      <LoginContent />
    </Suspense>
  );
}

