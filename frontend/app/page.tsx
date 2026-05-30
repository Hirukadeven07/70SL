import Link from 'next/link'
import { Suspense } from 'react'
import { fetchListings } from '@/lib/api'
import type { ListingFilters } from '@/lib/types'
import ListingCard from '@/components/ListingCard'
import SkeletonCard from '@/components/SkeletonCard'
import FilterSidebar from '@/components/FilterSidebar'
import MapViewWrapper from '@/components/MapViewWrapper'

const BODY_TYPE_PILLS = [
  { value: '',          label: 'All' },
  { value: '4x4',       label: '4×4 / 4WD' },
  { value: 'double_cab',label: 'Double Cab' },
  { value: 'suv',       label: 'SUV' },
] as const

interface PageProps {
  searchParams: ListingFilters
}

export default async function Page({ searchParams }: PageProps) {
  const data = await fetchListings({ page_size: '24', ...searchParams })
  const listings = data?.items ?? []
  const total    = data?.total ?? 0
  const page     = Number(searchParams.page ?? 1)
  const pages    = data?.pages ?? 1

  const activeBodyType = searchParams.body_type ?? ''

  function buildHref(patch: Partial<ListingFilters>) {
    const next = { ...searchParams, ...patch }
    const params = new URLSearchParams()
    for (const [k, v] of Object.entries(next)) {
      if (v) params.set(k, String(v))
    }
    return `/?${params.toString()}`
  }

  return (
    <>
      {/* Hero */}
      <section className="bg-gradient-to-br from-slate-900 via-brand-primary to-slate-800 py-14 px-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="font-display font-bold text-3xl sm:text-5xl text-white tracking-widest uppercase mb-2">
            Find Your 4×4
          </h1>
          <p className="text-slate-300 text-sm sm:text-base mb-8 max-w-xl">
            Sri Lanka&apos;s most complete database of 4×4 SUVs and double-cab pickups for sale.
            Updated daily from Ikman, Riyasewana, and Sarathi Ads.
          </p>

          {/* Body type quick-filter pills */}
          <div className="flex flex-wrap gap-2">
            {BODY_TYPE_PILLS.map(({ value, label }) => (
              <Link
                key={value}
                href={buildHref({ body_type: value || undefined, page: undefined })}
                className={`px-4 py-1.5 rounded-full text-sm font-semibold border transition-all duration-200 cursor-pointer
                  ${activeBodyType === value
                    ? 'bg-brand-cta border-brand-cta text-white'
                    : 'border-slate-500 text-slate-200 hover:border-white hover:text-white'
                  }`}
              >
                {label}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Main layout */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-6 items-start">
          {/* Filter sidebar — wrapped in Suspense because it uses useSearchParams */}
          <div className="hidden lg:block">
            <Suspense fallback={<div className="w-72 h-96 bg-white border border-slate-200 rounded-xl animate-pulse" />}>
              <FilterSidebar />
            </Suspense>
          </div>

          {/* Listing grid */}
          <main className="flex-1 min-w-0">
            {/* Results header */}
            <div className="flex items-center justify-between mb-5">
              <p className="text-sm text-brand-muted">
                {total > 0
                  ? <><span className="font-semibold text-brand-text">{total.toLocaleString()}</span> listings found</>
                  : 'No listings found'}
              </p>
              {total > 0 && pages > 1 && (
                <p className="text-xs text-brand-muted">Page {page} of {pages}</p>
              )}
            </div>

            {listings.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
                {listings.map((listing) => (
                  <ListingCard key={listing.id} listing={listing} />
                ))}
              </div>
            ) : (
              <EmptyState />
            )}

            {/* Pagination */}
            {pages > 1 && (
              <div className="flex justify-center gap-2 mt-10">
                {page > 1 && (
                  <Link
                    href={buildHref({ page: String(page - 1) })}
                    className="px-4 py-2 text-sm font-medium text-brand-text border border-slate-200 rounded hover:border-brand-cta hover:text-brand-cta transition-colors duration-200 cursor-pointer"
                  >
                    ← Previous
                  </Link>
                )}
                {page < pages && (
                  <Link
                    href={buildHref({ page: String(page + 1) })}
                    className="px-4 py-2 text-sm font-medium text-brand-text border border-slate-200 rounded hover:border-brand-cta hover:text-brand-cta transition-colors duration-200 cursor-pointer"
                  >
                    Next →
                  </Link>
                )}
              </div>
            )}
          </main>
        </div>

        {/* Map section */}
        {listings.length > 0 && (
          <section className="mt-12">
            <h2 className="text-sm font-bold text-brand-text uppercase tracking-widest mb-4">
              Listings by District
            </h2>
            <div className="h-96 rounded-xl border border-slate-200 overflow-hidden">
              <MapViewWrapper listings={listings} />
            </div>
          </section>
        )}
      </div>
    </>
  )
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      {/* Grid of skeleton cards to suggest shape */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5 w-full mb-10 opacity-30 pointer-events-none">
        {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
      </div>
      <p className="text-brand-muted text-sm">
        No listings found for your current filters.{' '}
        <Link href="/" className="text-brand-cta underline cursor-pointer">Clear filters</Link>
      </p>
    </div>
  )
}
