import { Card } from "@/components/ui/card";
import type { DemoMetric } from "@/lib/demo-data";
import { cn } from "@/lib/utils";

/**
 * Compact metric tile for dashboard/admin overviews. `metric.key` is emitted as a stable
 * data-metric hook for tests. Values are static demo data in Phase 1.
 */
export function MetricCard({ metric }: { metric: DemoMetric }) {
  const trendClass =
    metric.trend === "up"
      ? "text-success"
      : metric.trend === "down"
        ? "text-destructive"
        : "text-muted-foreground";

  return (
    <Card
      data-testid="metric-card"
      data-metric={metric.key}
      className="gap-2 py-5 transition-shadow hover:shadow-sm"
    >
      <div className="px-5">
        <p className="text-sm text-muted-foreground">{metric.label}</p>
        <p className="mt-1 text-3xl font-semibold tracking-tight tabular-nums">{metric.value}</p>
        {metric.delta ? (
          <p className={cn("mt-1 text-xs font-medium", trendClass)}>{metric.delta}</p>
        ) : null}
      </div>
    </Card>
  );
}
