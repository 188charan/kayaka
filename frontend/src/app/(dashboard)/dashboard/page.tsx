import type { Metadata } from "next";

import { ApiStatusClient } from "@/components/shared/api-status-client";
import { CheckIcon, ClockIcon } from "@/components/shared/icons";
import { MetricCard } from "@/components/shared/metric-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getServerMe } from "@/lib/auth/server";
import { DASHBOARD_ACTIVITY, DASHBOARD_METRICS, DASHBOARD_SETUP } from "@/lib/demo-data";

export const metadata: Metadata = { title: "Home" };

function firstName(fullName: string, email: string): string {
  const name = fullName.trim().split(/\s+/)[0];
  return name || email.split("@")[0] || "there";
}

export default async function DashboardHomePage() {
  const me = await getServerMe();
  const greetingName = me ? firstName(me.fullName, me.email) : "there";
  const done = DASHBOARD_SETUP.filter((step) => step.done).length;
  const setupPct = Math.round((done / DASHBOARD_SETUP.length) * 100);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">Good morning, {greetingName}</h1>
          <p className="text-muted-foreground">
            Your store at a glance. Metrics below are demo data for Phase 2.
          </p>
        </div>
        <ApiStatusClient />
      </div>

      {/* Metrics */}
      <section aria-label="Store metrics" className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {DASHBOARD_METRICS.map((metric) => (
          <MetricCard key={metric.key} metric={metric} />
        ))}
      </section>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Setup progress */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>Finish setting up your store</CardTitle>
            <Badge variant="brand">{setupPct}% done</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <div
              className="h-2 w-full overflow-hidden rounded-full bg-muted"
              role="progressbar"
              aria-valuenow={setupPct}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Store setup progress"
            >
              <div className="h-full rounded-full bg-brand" style={{ width: `${setupPct}%` }} />
            </div>
            <ul className="space-y-2">
              {DASHBOARD_SETUP.map((step) => (
                <li key={step.id} className="flex items-center gap-3 text-sm">
                  <span
                    aria-hidden="true"
                    className={
                      step.done
                        ? "grid size-5 place-items-center rounded-full bg-success text-success-foreground"
                        : "grid size-5 place-items-center rounded-full border"
                    }
                  >
                    {step.done ? <CheckIcon className="size-3.5" /> : null}
                  </span>
                  <span className={step.done ? "text-muted-foreground line-through" : undefined}>
                    {step.label}
                  </span>
                </li>
              ))}
            </ul>
            <Button variant="outline" size="sm">
              Continue setup
            </Button>
          </CardContent>
        </Card>

        {/* Recent activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              {DASHBOARD_ACTIVITY.map((item) => (
                <li key={item.id} className="flex gap-3">
                  <span
                    aria-hidden="true"
                    className="mt-0.5 grid size-7 shrink-0 place-items-center rounded-full bg-accent text-accent-foreground"
                  >
                    <ClockIcon className="size-4" />
                  </span>
                  <div className="space-y-0.5">
                    <p className="text-sm leading-snug">{item.text}</p>
                    <p className="text-xs text-muted-foreground">{item.time}</p>
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      <p className="text-xs text-muted-foreground">
        You&apos;re signed in. Your real catalog and live insights arrive in later phases; the
        metrics above are demo data.
      </p>
    </div>
  );
}
