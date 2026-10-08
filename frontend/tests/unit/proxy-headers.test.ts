import { describe, expect, it } from "vitest";

import {
  buildUpstreamHeaders,
  buildUpstreamUrl,
  clientIpFrom,
  newRequestId,
} from "@/lib/proxy-headers";

const SECRET = "s".repeat(32);

describe("buildUpstreamHeaders", () => {
  it("replaces spoofed proxy headers sent by the client", () => {
    const incoming = new Headers({
      "x-kayaka-proxy": "attacker-guess",
      "x-kayaka-client-ip": "1.2.3.4",
      cookie: "kayaka_session=abc",
    });
    const headers = buildUpstreamHeaders(incoming, { secret: SECRET, clientIp: null });
    expect(headers.get("x-kayaka-proxy")).toBe(SECRET);
    expect(headers.get("x-kayaka-client-ip")).toBeNull();
    expect(headers.get("cookie")).toBe("kayaka_session=abc");
  });

  it("sets the client IP when known", () => {
    const headers = buildUpstreamHeaders(new Headers(), {
      secret: SECRET,
      clientIp: "203.0.113.9",
    });
    expect(headers.get("x-kayaka-client-ip")).toBe("203.0.113.9");
  });

  it("keeps a well-formed request ID and replaces a malformed one", () => {
    const kept = buildUpstreamHeaders(new Headers({ "x-request-id": "edge-12345678" }), {
      secret: SECRET,
      clientIp: null,
    });
    expect(kept.get("x-request-id")).toBe("edge-12345678");

    const replaced = buildUpstreamHeaders(new Headers({ "x-request-id": "<bad id>" }), {
      secret: SECRET,
      clientIp: null,
    });
    expect(replaced.get("x-request-id")).toMatch(/^req_[0-9a-f]{32}$/);
  });
});

describe("clientIpFrom", () => {
  it("uses the first x-forwarded-for entry", () => {
    expect(clientIpFrom(new Headers({ "x-forwarded-for": "203.0.113.9, 10.0.0.1" }))).toBe(
      "203.0.113.9",
    );
  });

  it("falls back to x-real-ip and ignores invalid values", () => {
    expect(clientIpFrom(new Headers({ "x-real-ip": "2001:db8::1" }))).toBe("2001:db8::1");
    expect(clientIpFrom(new Headers({ "x-forwarded-for": "not-an-ip" }))).toBeNull();
    expect(clientIpFrom(new Headers())).toBeNull();
  });
});

describe("buildUpstreamUrl", () => {
  it("preserves path and query on the API origin", () => {
    const url = buildUpstreamUrl(
      new URL("http://localhost:3000/api/v1/public/ping?x=1"),
      "http://localhost:8000",
    );
    expect(url.toString()).toBe("http://localhost:8000/api/v1/public/ping?x=1");
  });
});

it("generates unique request IDs", () => {
  expect(newRequestId()).not.toBe(newRequestId());
});
