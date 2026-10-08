"use client";

import { Button } from "@/components/ui/button";

/** Shared body for route-level error.tsx boundaries. Never shows internal error details. */
export function ErrorState({
  title = "Something went wrong",
  message = "Please try again. If it keeps happening, let us know.",
  digest,
  onRetry,
}: {
  title?: string;
  message?: string;
  digest?: string;
  onRetry?: () => void;
}) {
  return (
    <div
      role="alert"
      className="mx-auto flex max-w-md flex-col items-center gap-4 py-16 text-center"
    >
      <h1 className="text-xl font-semibold">{title}</h1>
      <p className="text-muted-foreground">{message}</p>
      {onRetry ? (
        <Button size="lg" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
      {digest ? <p className="text-xs text-muted-foreground">Reference: {digest}</p> : null}
    </div>
  );
}
