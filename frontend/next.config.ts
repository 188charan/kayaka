import type { NextConfig } from "next";

const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  // SAMEORIGIN, not DENY: the dashboard will preview the storefront in an iframe (Phase 7).
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
];

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  async headers() {
    return [
      // /api/* responses come from Django, which sets its own (stricter) headers.
      { source: "/((?!api/).*)", headers: securityHeaders },
    ];
  },
};

export default nextConfig;
