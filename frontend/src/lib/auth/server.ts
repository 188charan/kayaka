import "server-only";

import { cookies } from "next/headers";

import { serverEnv } from "@/lib/env";
import { PROXY_SECRET_HEADER } from "@/lib/proxy-headers";

import type { Me } from "./types";

/**
 * Resolve the authenticated identity on the server (for server components and layout guards).
 *
 * Calls Django directly (server-to-server) with the proxy secret, forwarding the browser's
 * cookies — including the HttpOnly session cookie — so Django can authenticate the request. The
 * session cookie is never read by client JavaScript. Returns null when unauthenticated (401).
 */
export async function getServerMe(): Promise<Me | null> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore
    .getAll()
    .map((cookie) => `${cookie.name}=${cookie.value}`)
    .join("; ");

  let response: Response;
  try {
    response = await fetch(`${serverEnv.API_ORIGIN}/api/v1/me`, {
      headers: {
        [PROXY_SECRET_HEADER]: serverEnv.PROXY_SHARED_SECRET,
        cookie: cookieHeader,
      },
      cache: "no-store",
    });
  } catch {
    return null; // backend unreachable: treat as unauthenticated for guard purposes
  }

  if (response.status !== 200) return null;
  const body = (await response.json()) as { data: Me };
  return body.data;
}
