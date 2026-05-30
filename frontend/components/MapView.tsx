'use client'

import { useEffect, useRef } from 'react'
import 'leaflet/dist/leaflet.css'
import type { Listing, DistrictCentroid } from '@/lib/types'

interface Props {
  listings: Listing[]
}

export default function MapView({ listings }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<unknown>(null)

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    let map: ReturnType<typeof import('leaflet')['map']>

    async function initMap() {
      const L = (await import('leaflet')).default

      // Fix Leaflet default marker icon path in webpack/Next.js
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      delete (L.Icon.Default.prototype as any)._getIconUrl
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
        iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
        shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
      })

      if (!containerRef.current) return
      map = L.map(containerRef.current).setView([7.8731, 80.7718], 7)
      mapRef.current = map

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 18,
      }).addTo(map)

      const centroids: Record<string, DistrictCentroid> = await fetch('/district_centroids.json').then((r) => r.json())

      const countByDistrict = listings.reduce<Record<string, number>>((acc, l) => {
        if (l.district) acc[l.district] = (acc[l.district] ?? 0) + 1
        return acc
      }, {})

      for (const [district, centroid] of Object.entries(centroids)) {
        const count = countByDistrict[district] ?? 0
        if (count === 0) continue

        const marker = L.circleMarker([centroid.lat, centroid.lng], {
          radius: Math.min(6 + count * 1.5, 20),
          fillColor: '#DC2626',
          color: '#fff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.85,
        }).addTo(map)

        marker.bindPopup(
          `<strong>${centroid.name}</strong><br/>${count} listing${count !== 1 ? 's' : ''}`
        )
      }
    }

    initMap()

    return () => {
      if (map) {
        map.remove()
        mapRef.current = null
      }
    }
  }, [listings])

  return (
    <div
      ref={containerRef}
      className="w-full h-full"
      aria-label="Map showing listing locations across Sri Lanka"
    />
  )
}
