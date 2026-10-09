import type { Metadata } from "next";
import { Suspense } from "react";

import { Skeleton } from "@/components/ui/skeleton";

import { LoginForm } from "./login-form";

export const metadata: Metadata = {
  title: "Sign in",
  robots: { index: false, follow: false },
};

export default function LoginPage() {
  return (
    <main className="relative flex min-h-dvh items-center justify-center overflow-hidden px-4 py-16">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(60%_50%_at_50%_-10%,var(--brand)_0%,transparent_60%)] opacity-15"
      />
      <Suspense fallback={<Skeleton className="h-96 w-full max-w-sm rounded-xl" />}>
        <LoginForm />
      </Suspense>
    </main>
  );
}
