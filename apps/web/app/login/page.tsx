"use client";

import { useSearchParams } from "next/navigation";
import LoginForm from "./LoginForm";

export default function LoginPage() {
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get("redirect") || "/dashboard";

  return <LoginForm redirectTo={redirectTo} />;
}

