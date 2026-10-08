"use client";

import { ErrorState } from "@/components/shared/error-state";

export default function StoreError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <ErrorState
      title="This store couldn't load"
      message="Please check your connection and try again."
      digest={error.digest}
      onRetry={reset}
    />
  );
}
