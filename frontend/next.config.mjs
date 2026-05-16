/** @type {import('next').NextConfig} */

const backendPort = process.env.BACKEND_PORT || "8000";

const SECURITY_HEADERS = [
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-XSS-Protection", value: "1; mode=block" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' data: blob:",
      "font-src 'self' https://fonts.gstatic.com",
      `connect-src 'self' http://localhost:${backendPort} ws://localhost:*`,
    ].join("; "),
  },
];

const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // Transpile workspace packages
  transpilePackages: [
    "@alphaforge/solar-orb-ui",
    "@alphaforge/solar-orb-ball",
    "@alphaforge/logger",
  ],
  async headers() {
    return [{ source: "/(.*)", headers: SECURITY_HEADERS }];
  },
  // Proxy API calls to backend in development
  async rewrites() {
    return [
      {
        // Proxy everything under /api/ to the backend, EXCEPT /api/v1/chat
        // which is handled by the Next.js API route at app/api/v1/chat/route.ts
        // (that route manually forwards the Authorization header, which
        // Next.js rewrites strip).
        source: "/api/:path((?!v1/chat(?:/|$)).*)",
        destination: `http://localhost:${backendPort}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
