import { cn } from "@/lib/utils";

export type Status = "loading" | "ok" | "error";

const dotClass: Record<Status, string> = {
  loading: "bg-muted-foreground animate-pulse",
  ok: "bg-success",
  error: "bg-destructive",
};

export function StatusBadge({
  status,
  label,
  testId = "api-status",
}: {
  status: Status;
  label: string;
  testId?: string;
}) {
  return (
    <p
      role="status"
      data-testid={testId}
      data-state={status}
      className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-sm"
    >
      <span aria-hidden="true" className={cn("size-2 rounded-full", dotClass[status])} />
      {label}
    </p>
  );
}
