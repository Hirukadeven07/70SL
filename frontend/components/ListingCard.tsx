import type { Listing } from '@/lib/types'

const SOURCE_BADGE: Record<string, { label: string; classes: string }> = {
  ikman:      { label: 'Ikman',      classes: 'bg-blue-600 text-white' },
  riyasewana: { label: 'Riyasewana', classes: 'bg-emerald-600 text-white' },
  sarathiads: { label: 'Sarathi',    classes: 'bg-amber-500 text-white' },
}

const BODY_LABEL: Record<string, string> = {
  '4x4':       '4×4',
  double_cab:  'DOUBLE CAB',
  suv:         'SUV',
}

function formatPrice(lkr: number | null): string {
  if (lkr == null) return 'Price on request'
  return `Rs. ${lkr.toLocaleString('en-LK')}`
}

function formatMileage(km: number | null): string {
  if (km == null) return '—'
  return km >= 1000 ? `${(km / 1000).toFixed(0)}k km` : `${km} km`
}

interface Props {
  listing: Listing
}

export default function ListingCard({ listing }: Props) {
  const thumb = listing.image_urls[0] ?? null
  const source = SOURCE_BADGE[listing.source] ?? { label: listing.source, classes: 'bg-slate-600 text-white' }

  return (
    <article className="group bg-white rounded-xl border border-slate-200 overflow-hidden hover:shadow-xl hover:border-slate-300 transition-all duration-200 cursor-pointer">
      {/* Image */}
      <div className="relative aspect-[16/9] bg-slate-100 overflow-hidden">
        {thumb ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={thumb}
            alt={listing.title}
            loading="lazy"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              const target = e.currentTarget
              target.style.display = 'none'
            }}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <svg className="w-16 h-16 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}

        {/* Body type badge */}
        {listing.body_type && (
          <span className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold tracking-wider bg-brand-cta text-white uppercase">
            {BODY_LABEL[listing.body_type] ?? listing.body_type}
          </span>
        )}

        {/* Source badge */}
        <span className={`absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-bold tracking-wide uppercase ${source.classes}`}>
          {source.label}
        </span>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        <h3 className="text-sm font-semibold text-brand-text leading-snug line-clamp-2 group-hover:text-brand-cta transition-colors duration-200">
          {listing.title}
        </h3>

        {/* Price */}
        <p className="font-mono text-xl font-bold text-brand-cta">
          {formatPrice(listing.price_lkr)}
        </p>

        {/* Spec chips */}
        <div className="flex flex-wrap gap-1.5">
          {listing.year && (
            <Chip>{listing.year}</Chip>
          )}
          {listing.mileage_km != null && (
            <Chip>{formatMileage(listing.mileage_km)}</Chip>
          )}
          {listing.fuel_type && (
            <Chip className="capitalize">{listing.fuel_type}</Chip>
          )}
          {listing.transmission && (
            <Chip className="capitalize">{listing.transmission}</Chip>
          )}
        </div>

        {/* District + link row */}
        <div className="flex items-center justify-between pt-1">
          {listing.district && (
            <span className="flex items-center gap-1 text-xs text-brand-muted">
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="capitalize">{listing.district}</span>
            </span>
          )}
          <a
            href={listing.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-brand-cta hover:underline font-medium cursor-pointer"
            onClick={(e) => e.stopPropagation()}
          >
            View original →
          </a>
        </div>
      </div>
    </article>
  )
}

function Chip({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-600 ${className}`}>
      {children}
    </span>
  )
}
