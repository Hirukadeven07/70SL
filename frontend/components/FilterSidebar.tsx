'use client'

import { useRouter, useSearchParams, usePathname } from 'next/navigation'
import { useCallback } from 'react'

const DISTRICTS = [
  'Colombo','Gampaha','Kalutara','Kandy','Matale','Nuwara Eliya',
  'Galle','Matara','Hambantota','Jaffna','Kilinochchi','Mannar',
  'Mullaitivu','Vavuniya','Trincomalee','Batticaloa','Ampara',
  'Badulla','Monaragala','Ratnapura','Kegalle','Kurunegala',
  'Puttalam','Anuradhapura','Polonnaruwa',
]

const MAKES = [
  'Toyota','Mitsubishi','Ford','Isuzu','Nissan','Land Rover',
  'Suzuki','Jeep','Mercedes-Benz','BMW','Kia','Hyundai',
]

export default function FilterSidebar() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const get = useCallback((key: string) => searchParams.get(key) ?? '', [searchParams])

  function applyFilters(form: HTMLFormElement) {
    const data = new FormData(form)
    const params = new URLSearchParams()
    for (const [key, value] of Array.from(data.entries())) {
      if (typeof value === 'string' && value.trim()) {
        params.set(key, value.trim())
      }
    }
    params.delete('page')
    router.push(`${pathname}?${params.toString()}`)
  }

  function resetFilters() {
    router.push(pathname)
  }

  const bodyTypes = ['4x4', 'double_cab', 'suv'] as const
  const bodyTypeLabels: Record<string, string> = {
    '4x4': '4×4 / 4WD / AWD',
    double_cab: 'Double Cab Pickup',
    suv: 'SUV',
  }

  return (
    <aside className="w-72 shrink-0">
      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden sticky top-20">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 bg-brand-primary">
          <h2 className="text-sm font-bold text-white uppercase tracking-widest">Filters</h2>
          <button
            type="button"
            onClick={resetFilters}
            className="text-xs text-slate-400 hover:text-white transition-colors duration-200 cursor-pointer"
          >
            Reset all
          </button>
        </div>

        <form
          onSubmit={(e) => { e.preventDefault(); applyFilters(e.currentTarget) }}
          className="divide-y divide-slate-100"
        >
          {/* Body type */}
          <fieldset className="px-4 py-4">
            <legend className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-3">Body Type</legend>
            <div className="space-y-2">
              {bodyTypes.map((bt) => (
                <label key={bt} className="flex items-center gap-2.5 cursor-pointer group">
                  <input
                    type="radio"
                    name="body_type"
                    value={bt}
                    defaultChecked={get('body_type') === bt}
                    className="accent-brand-cta w-4 h-4"
                  />
                  <span className="text-sm text-brand-text group-hover:text-brand-cta transition-colors duration-150">
                    {bodyTypeLabels[bt]}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>

          {/* Price range */}
          <fieldset className="px-4 py-4">
            <legend className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-3">Price (LKR)</legend>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                name="price_min"
                placeholder="Min"
                defaultValue={get('price_min')}
                min={0}
                className="w-full px-2.5 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-brand-cta"
              />
              <input
                type="number"
                name="price_max"
                placeholder="Max"
                defaultValue={get('price_max')}
                min={0}
                className="w-full px-2.5 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-brand-cta"
              />
            </div>
          </fieldset>

          {/* Year range */}
          <fieldset className="px-4 py-4">
            <legend className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-3">Year</legend>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                name="year_min"
                placeholder="From"
                defaultValue={get('year_min')}
                min={1990}
                max={2025}
                className="w-full px-2.5 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-brand-cta"
              />
              <input
                type="number"
                name="year_max"
                placeholder="To"
                defaultValue={get('year_max')}
                min={1990}
                max={2025}
                className="w-full px-2.5 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-brand-cta"
              />
            </div>
          </fieldset>

          {/* District */}
          <fieldset className="px-4 py-4">
            <legend className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-3">District</legend>
            <select
              name="district"
              defaultValue={get('district')}
              className="w-full px-2.5 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-brand-cta bg-white cursor-pointer"
            >
              <option value="">All districts</option>
              {DISTRICTS.map((d) => (
                <option key={d} value={d.toLowerCase()}>{d}</option>
              ))}
            </select>
          </fieldset>

          {/* Fuel type */}
          <fieldset className="px-4 py-4">
            <legend className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-3">Fuel Type</legend>
            <div className="space-y-2">
              {['petrol', 'diesel', 'hybrid'].map((ft) => (
                <label key={ft} className="flex items-center gap-2.5 cursor-pointer group">
                  <input
                    type="radio"
                    name="fuel_type"
                    value={ft}
                    defaultChecked={get('fuel_type') === ft}
                    className="accent-brand-cta w-4 h-4"
                  />
                  <span className="text-sm text-brand-text capitalize group-hover:text-brand-cta transition-colors duration-150">
                    {ft}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>

          {/* Transmission */}
          <fieldset className="px-4 py-4">
            <legend className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-3">Transmission</legend>
            <div className="flex gap-4">
              {['manual', 'automatic'].map((t) => (
                <label key={t} className="flex items-center gap-2 cursor-pointer group">
                  <input
                    type="radio"
                    name="transmission"
                    value={t}
                    defaultChecked={get('transmission') === t}
                    className="accent-brand-cta w-4 h-4"
                  />
                  <span className="text-sm text-brand-text capitalize group-hover:text-brand-cta transition-colors duration-150">
                    {t}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>

          {/* Make */}
          <fieldset className="px-4 py-4">
            <legend className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-3">Make</legend>
            <select
              name="make"
              defaultValue={get('make')}
              className="w-full px-2.5 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-brand-cta bg-white cursor-pointer"
            >
              <option value="">Any make</option>
              {MAKES.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </fieldset>

          {/* Sort */}
          <fieldset className="px-4 py-4">
            <legend className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-3">Sort By</legend>
            <select
              name="sort"
              defaultValue={get('sort') || 'newest'}
              className="w-full px-2.5 py-1.5 text-sm border border-slate-200 rounded focus:outline-none focus:border-brand-cta bg-white cursor-pointer"
            >
              <option value="newest">Newest first</option>
              <option value="price_asc">Price: low to high</option>
              <option value="price_desc">Price: high to low</option>
            </select>
          </fieldset>

          {/* Apply button */}
          <div className="px-4 py-4">
            <button
              type="submit"
              className="w-full py-2.5 bg-brand-cta text-white text-sm font-bold uppercase tracking-widest rounded hover:bg-red-700 transition-colors duration-200 cursor-pointer"
            >
              Apply Filters
            </button>
          </div>
        </form>
      </div>
    </aside>
  )
}
