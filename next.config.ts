import type { NextConfig } from "next";
const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
  {
    key: "Content-Security-Policy",
    value:
      "default-src 'self'; script-src 'self' 'unsafe-inline'" +
      (process.env.NODE_ENV === "development" ? " 'unsafe-eval'" : "") +
      "; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self'; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'",
  },
];
const nextConfig: NextConfig = {
  output: "standalone",
  outputFileTracingExcludes: {
    "*": ["./private/**/*", "./qa/**/*", "./deploy-artifacts/**/*"],
  },
  poweredByHeader: false,
  async headers() {
    return [
      { source: "/:path*", headers: securityHeaders },
      {
        source: "/demo/:path*",
        headers: [
          { key: "Cache-Control", value: "private, no-store, max-age=0" },
          { key: "X-Robots-Tag", value: "noindex, nofollow, noarchive" },
        ],
      },
    ];
  },
  async redirects() {
    return [
      {
        source: "/videos.html",
        destination: "/demo/video.html",
        permanent: false,
      },
      { source: "/videos", destination: "/demo/bibliothek", permanent: false },
      {
        source: "/video.html",
        destination: "/demo/video.html",
        permanent: false,
      },
      {
        source: "/VIDEOS.html",
        destination: "/demo/video.html",
        permanent: false,
      },
    ];
  },
};
export default nextConfig;
