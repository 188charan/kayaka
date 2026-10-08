import createClient from "openapi-fetch";

import type { paths } from "@/lib/api/schema";

/**
 * Typed API client for client components. Uses relative URLs, so every call goes to this
 * origin's /api/v1/* and through src/proxy.ts to Django (ADR 0003). Cookies are same-origin.
 */
export const browserApi = createClient<paths>({ baseUrl: "", credentials: "same-origin" });
