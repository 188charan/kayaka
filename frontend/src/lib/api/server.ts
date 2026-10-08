import "server-only";

import createClient from "openapi-fetch";

import type { paths } from "@/lib/api/schema";
import { serverEnv } from "@/lib/env";
import { PROXY_SECRET_HEADER } from "@/lib/proxy-headers";

/**
 * Typed API client for server components and route handlers. Calls Django directly
 * (server-to-server) and identifies itself with the proxy secret (ADR 0003).
 */
export const serverApi = createClient<paths>({
  baseUrl: serverEnv.API_ORIGIN,
  headers: { [PROXY_SECRET_HEADER]: serverEnv.PROXY_SHARED_SECRET },
});
