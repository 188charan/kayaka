import { NextResponse, type NextRequest } from "next/server";

import { serverEnv } from "@/lib/env";
import { buildUpstreamHeaders, buildUpstreamUrl, clientIpFrom } from "@/lib/proxy-headers";

/**
 * Same-origin API proxy (ADR 0003): the browser calls /api/v1/* on this origin and we forward
 * to Django, attaching the proxy secret and the client IP. No CORS, no third-party cookies.
 */
export function proxy(request: NextRequest) {
  const upstream = buildUpstreamUrl(request.nextUrl, serverEnv.API_ORIGIN);
  const headers = buildUpstreamHeaders(request.headers, {
    secret: serverEnv.PROXY_SHARED_SECRET,
    clientIp: clientIpFrom(request.headers),
  });
  return NextResponse.rewrite(upstream, { request: { headers } });
}

export const config = {
  matcher: "/api/v1/:path*",
};
