"use client";

import "./globals.css";

import { ErrorState } from "@/components/shared/error-state";

/** Last-resort boundary for errors in the root layout itself. Must render its own <html>. */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <html lang="en">
      <body className="min-h-dvh px-4">
        <ErrorState digest={error.digest} onRetry={reset} />
      </body>
    </html>
  );
}
