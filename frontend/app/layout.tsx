import type { Metadata } from 'next'
import localFont from 'next/font/local'
import { Syncopate } from 'next/font/google'
import Navbar from '@/components/Navbar'
import './globals.css'

const geistSans = localFont({
  src: './fonts/GeistVF.woff',
  variable: '--font-geist-sans',
  weight: '100 900',
})

const geistMono = localFont({
  src: './fonts/GeistMonoVF.woff',
  variable: '--font-geist-mono',
  weight: '100 900',
})

const syncopate = Syncopate({
  weight: ['400', '700'],
  subsets: ['latin'],
  variable: '--font-syncopate',
})

export const metadata: Metadata = {
  title: '70SL | Sri Lanka 4x4 & Double-Cab Listings',
  description:
    "Sri Lanka's largest database of 4x4 SUVs and double-cab pickup trucks for sale.",
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${syncopate.variable} font-sans antialiased bg-brand-bg text-brand-text`}
      >
        <Navbar />
        {children}
      </body>
    </html>
  )
}
