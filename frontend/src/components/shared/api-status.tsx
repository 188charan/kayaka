import { connection } from "next/server";

import { StatusBadge, type Status } from "@/components/shared/status-badge";
import { ApiError, unwrap } from "@/lib/api/errors";
import { serverApi } from "@/lib/api/server";

async function checkApi(): Promise<{ status: Status; label: string }> {
  try {
    const { data } = await unwrap(serverApi.GET("/api/v1/public/ping", { cache: "no-store" }));
    return { status: "ok", label: `API connected · ${data.version} (${data.environment})` };
  } catch (error) {
    const code = error instanceof ApiError ? error.code : "UNKNOWN";
    return { status: "error", label: `API unreachable (${code})` };
  }
}

/** Server component: proves the server → Django path works. Rendered per request. */
export async function ApiStatus() {
  await connection(); // never prerender at build time; the API may not be running then
  const { status, label } = await checkApi();
  return <StatusBadge status={status} label={label} testId="api-status-server" />;
}
