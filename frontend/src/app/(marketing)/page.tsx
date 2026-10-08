import Link from "next/link";
import { Suspense } from "react";

import { ApiStatus } from "@/components/shared/api-status";
import { StatusBadge } from "@/components/shared/status-badge";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-2xl flex-col justify-center gap-8 px-4 py-16">
      <div className="space-y-3">
        <h1 className="text-4xl font-semibold tracking-tight">Kayaka</h1>
        <p className="text-lg text-muted-foreground">
          A persistent, searchable online store for small businesses — browse, add to cart, and send
          an inquiry on WhatsApp.
        </p>
      </div>

      <Suspense fallback={<StatusBadge status="loading" label="Checking API…" />}>
        <ApiStatus />
      </Suspense>

      <nav aria-label="Surfaces" className="flex flex-col gap-3 sm:flex-row">
        <Button asChild size="lg">
          <Link href="/store/demo-store">Demo storefront</Link>
        </Button>
        <Button asChild size="lg" variant="outline">
          <Link href="/dashboard">Tenant dashboard</Link>
        </Button>
        <Button asChild size="lg" variant="outline">
          <Link href="/admin">Platform admin</Link>
        </Button>
      </nav>

      <p className="text-sm text-muted-foreground">Phase 1 · walking skeleton</p>
    </main>
  );
}
