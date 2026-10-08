import { isIP } from "node:net";

/**
 * Pure helpers for the /api/v1 proxy (src/proxy.ts). See ADR 0003.
 *
 * Every request forwarded to Django gets:
 *   X-Kayaka-Proxy      shared secret, so Django knows the request came through us
 *   X-Kayaka-Client-IP  the browser's IP as seen by our edge
 *   X-Request-ID        preserved if well-formed, otherwise generated
 * Values a client sends for the two X-Kayaka-* headers are always discarded.
 */

export const PROXY_SECRET_HEADER = "x-kayaka-proxy";
export const CLIENT_IP_HEADER = "x-kayaka-client-ip";
export const REQUEST_ID_HEADER = "x-request-id";

const VALID_REQUEST_ID = /^[A-Za-z0-9._-]{8,128}$/;

export function newRequestId(): string {
  return `req_${crypto.randomUUID().replaceAll("-", "")}`;
}

/**
 * The client IP as reported by the hosting edge. On Vercel, `x-forwarded-for` is set by the
 * platform and cannot be spoofed by the client. Invalid values are ignored.
 */
export function clientIpFrom(headers: Headers): string | null {
  const forwarded = headers.get("x-forwarded-for")?.split(",")[0]?.trim();
  const candidate = forwarded || headers.get("x-real-ip")?.trim();
  return candidate && isIP(candidate) ? candidate : null;
}

export function buildUpstreamUrl(requestUrl: URL, apiOrigin: string): URL {
  return new URL(`${requestUrl.pathname}${requestUrl.search}`, apiOrigin);
}

export function buildUpstreamHeaders(
  incoming: Headers,
  options: { secret: string; clientIp: string | null },
): Headers {
  const headers = new Headers(incoming);
  headers.delete(PROXY_SECRET_HEADER);
  headers.delete(CLIENT_IP_HEADER);

  headers.set(PROXY_SECRET_HEADER, options.secret);
  if (options.clientIp) {
    headers.set(CLIENT_IP_HEADER, options.clientIp);
  }

  const requestId = incoming.get(REQUEST_ID_HEADER);
  headers.set(
    REQUEST_ID_HEADER,
    requestId && VALID_REQUEST_ID.test(requestId) ? requestId : newRequestId(),
  );
  return headers;
}
