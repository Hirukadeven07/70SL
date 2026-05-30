'use client'

import dynamic from 'next/dynamic'
import type { Listing } from '@/lib/types'

const MapView = dynamic(() => import('./MapView'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center bg-slate-100 rounded-xl">
      <span className="text-sm text-brand-muted animate-pulse">Loading map…</span>
    </div>
  ),
})

export default function MapViewWrapper({ listings }: { listings: Listing[] }) {
  return <MapView listings={listings} />
}
