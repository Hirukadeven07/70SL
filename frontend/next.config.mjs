/** @type {import('next').NextConfig} */

const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const securityHeaders = [
  { key: 'X-DNS-Prefetch-Control', value: 'on' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      // Next.js requires unsafe-eval (dev HMR) and unsafe-inline (RSC hydration)
      "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
      "style-src 'self' 'unsafe-inline'",
      // Allow images from all listing sources + Supabase + OSM tiles (Leaflet)
      [
        "img-src 'self' data: blob:",
        'https://*.ikman.lk',
        'https://*.riyasewana.com',
        'https://*.sarathiads.lk',
        'https://*.supabase.co',
        'https://*.tile.openstreetmap.org',
      ].join(' '),
      "font-src 'self'",
      // Allow fetch to API and OSM tile CDN
      `connect-src 'self' ${apiUrl} https://*.tile.openstreetmap.org`,
      "frame-ancestors 'none'",
    ].join('; '),
  },
]

const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ]
  },
  images: {
    remotePatterns: [
      { hostname: '**.ikman.lk' },
      { hostname: '**.riyasewana.com' },
      { hostname: '**.sarathiads.lk' },
      { hostname: '**.supabase.co' },
    ],
  },
}

export default nextConfig
