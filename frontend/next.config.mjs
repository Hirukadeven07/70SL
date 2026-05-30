/** @type {import('next').NextConfig} */
const nextConfig = {
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
