'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'

export default function Navbar() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)

  const links = [
    { href: '/', label: 'Listings' },
    { href: '/alerts', label: 'Alerts' },
  ]

  return (
    <nav className="sticky top-0 z-50 bg-brand-primary shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <span className="font-display font-bold text-2xl text-white tracking-widest group-hover:text-red-400 transition-colors duration-200">
              70SL
            </span>
            <span className="hidden sm:block text-xs text-slate-400 uppercase tracking-widest leading-tight">
              Sri Lanka<br />4×4 Listings
            </span>
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-1">
            {links.map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                className={`px-4 py-2 rounded text-sm font-medium tracking-wide transition-colors duration-200 cursor-pointer
                  ${pathname === href
                    ? 'bg-brand-cta text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-700'
                  }`}
              >
                {label}
              </Link>
            ))}
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded text-slate-300 hover:text-white hover:bg-slate-700 transition-colors duration-200 cursor-pointer"
            onClick={() => setOpen(!open)}
            aria-label="Toggle menu"
          >
            <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {open ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden border-t border-slate-700 bg-brand-primary">
          <div className="px-4 py-2 space-y-1">
            {links.map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setOpen(false)}
                className={`block px-3 py-2 rounded text-sm font-medium transition-colors duration-200 cursor-pointer
                  ${pathname === href
                    ? 'bg-brand-cta text-white'
                    : 'text-slate-300 hover:text-white hover:bg-slate-700'
                  }`}
              >
                {label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  )
}
