import type { Metadata } from "next";
import { Suspense } from "react";

import { ApiStatus } from "@/components/shared/api-status";
import { MetricCard } from "@/components/shared/metric-card";
import { StatusBadge } from "@/components/shared/status-badge";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ADMIN_AUDIT, ADMIN_HEALTH, ADMIN_METRICS, ADMIN_RECENT_TENANTS } from "@/lib/demo-data";

export const metadata: Metadata = { title: "Overview" };

const statusBadge = {
  Active: "success",
  Trial: "brand",
  Suspended: "muted",
} as const;

export default function AdminOverviewPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Platform overview</h1>
          <p className="text-sm text-muted-foreground">
            Operations across every Kayaka tenant. Demo data in Phase 1.
          </p>
        </div>
        <Suspense fallback={<StatusBadge status="loading" label="Checking API…" />}>
          <ApiStatus />
        </Suspense>
      </div>

      {/* Metrics */}
      <section aria-label="Platform metrics" className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {ADMIN_METRICS.map((metric) => (
          <MetricCard key={metric.key} metric={metric} />
        ))}
      </section>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Recent tenants */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent tenants</CardTitle>
            <CardDescription>Latest businesses to join the platform</CardDescription>
          </CardHeader>
          <CardContent className="px-0">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-y text-left text-xs text-muted-foreground">
                  <th className="px-6 py-2 font-medium">Tenant</th>
                  <th className="px-3 py-2 font-medium">Plan</th>
                  <th className="px-3 py-2 font-medium">Status</th>
                  <th className="px-6 py-2 text-right font-medium">Joined</th>
                </tr>
              </thead>
              <tbody>
                {ADMIN_RECENT_TENANTS.map((tenant) => (
                  <tr key={tenant.id} className="border-b last:border-0">
                    <td className="px-6 py-3 font-medium">{tenant.name}</td>
                    <td className="px-3 py-3 text-muted-foreground">{tenant.plan}</td>
                    <td className="px-3 py-3">
                      <Badge variant={statusBadge[tenant.status as keyof typeof statusBadge]}>
                        {tenant.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-3 text-right text-muted-foreground">{tenant.joined}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        {/* System health */}
        <Card>
          <CardHeader>
            <CardTitle>System health</CardTitle>
            <CardDescription>Live platform status</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {ADMIN_HEALTH.map((svc) => {
                const operational = svc.status === "Operational";
                return (
                  <li key={svc.id} className="flex items-center justify-between gap-2">
                    <span className="flex items-center gap-2 text-sm">
                      <span
                        aria-hidden="true"
                        className={
                          operational
                            ? "size-2 rounded-full bg-success"
                            : "size-2 rounded-full bg-amber-500"
                        }
                      />
                      {svc.label}
                    </span>
                    <span className="text-xs text-muted-foreground">{svc.detail}</span>
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Usage summary */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Usage summary</CardTitle>
            <CardDescription>Last 7 days across the platform</CardDescription>
          </CardHeader>
          <CardContent>
            <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                { label: "Storefront views", value: "48,210" },
                { label: "Searches", value: "9,044" },
                { label: "Inquiries", value: "612" },
                { label: "WhatsApp handoffs", value: "418" },
              ].map((stat) => (
                <div key={stat.label}>
                  <dt className="text-xs text-muted-foreground">{stat.label}</dt>
                  <dd className="mt-1 text-xl font-semibold tabular-nums">{stat.value}</dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>

        {/* Audit activity preview */}
        <Card>
          <CardHeader>
            <CardTitle>Audit activity</CardTitle>
            <CardDescription>Recent platform events</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3 text-sm">
              {ADMIN_AUDIT.map((entry) => (
                <li key={entry.id} className="flex items-start justify-between gap-3">
                  <div className="space-y-0.5">
                    <p className="leading-snug">{entry.action}</p>
                    <p className="text-xs text-muted-foreground">{entry.actor}</p>
                  </div>
                  <span className="shrink-0 text-xs text-muted-foreground">{entry.time}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
