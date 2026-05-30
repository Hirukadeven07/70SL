import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        brand: {
          primary:   '#1E293B',
          secondary: '#334155',
          cta:       '#DC2626',
          bg:        '#F8FAFC',
          text:      '#0F172A',
          muted:     '#64748B',
        },
      },
      fontFamily: {
        display: ['var(--font-syncopate)', 'sans-serif'],
        sans:    ['var(--font-geist-sans)', 'sans-serif'],
        mono:    ['var(--font-geist-mono)', 'monospace'],
      },
    },
  },
  plugins: [],
}

export default config
