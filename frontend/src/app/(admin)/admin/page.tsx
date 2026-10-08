import type { Metadata } from "next";
import { Suspense } from "react";

import { ApiStatus } from "@/components/shared/api-status";
import { StatusBadge } from "@/components/shared/status-badge";

export const metadata: Metadata = { title: "Overview" };

const METRICS = ["Tenants", "Active tenants", "Products", "Inquiries (7d)"];

export default function AdminOverviewPage() {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-semibold">Platform overview</h1>
        <Suspense fallback={<StatusBadge status="loading" label="Checking API…" />}>
          <ApiStatus />
        </Suspense>
      </div>
      <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {METRICS.map((label) => (
          <div key={label} className="rounded-lg border bg-background p-4">
            <dt className="text-xs text-muted-foreground">{label}</dt>
            <dd className="mt-1 text-2xl font-semibold">—</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
