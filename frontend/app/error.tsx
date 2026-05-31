'use client'

import { useEffect } from 'react'
import Link from 'next/link'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Page error:', error)
  }, [error])

  return (
    <div className="max-w-7xl mx-auto px-4 py-24 text-center">
      <h2 className="text-xl font-bold text-brand-text mb-3">
        Something went wrong
      </h2>
      <p className="text-sm text-brand-muted mb-2">
        {error.message || 'An unexpected error occurred.'}
      </p>
      {error.digest && (
        <p className="text-xs text-slate-400 mb-6 font-mono">
          Digest: {error.digest}
        </p>
      )}
      <div className="flex justify-center gap-4">
        <button
          onClick={reset}
          className="px-4 py-2 bg-brand-cta text-white text-sm font-semibold rounded hover:bg-red-700 transition-colors cursor-pointer"
        >
          Try again
        </button>
        <Link
          href="/"
          className="px-4 py-2 border border-slate-300 text-sm font-semibold rounded hover:border-brand-cta hover:text-brand-cta transition-colors cursor-pointer"
        >
          Go home
        </Link>
      </div>
    </div>
  )
}
