"use client";

import { useEffect, useState } from "react";

import { StatusBadge, type Status } from "@/components/shared/status-badge";
import { browserApi } from "@/lib/api/browser";
import { ApiError, unwrap } from "@/lib/api/errors";

/** Client component: proves the browser → proxy → Django path works. */
export function ApiStatusClient() {
  const [state, setState] = useState<{ status: Status; label: string }>({
    status: "loading",
    label: "Checking API…",
  });

  useEffect(() => {
    let cancelled = false;
    unwrap(browserApi.GET("/api/v1/public/ping"))
      .then(({ data }) => {
        if (!cancelled)
          setState({ status: "ok", label: `API reachable via proxy · ${data.version}` });
      })
      .catch((error: unknown) => {
        const code = error instanceof ApiError ? error.code : "UNKNOWN";
        if (!cancelled) setState({ status: "error", label: `API unreachable (${code})` });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return <StatusBadge status={state.status} label={state.label} testId="api-status-proxy" />;
}
