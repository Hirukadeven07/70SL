'use client'

import { useState } from 'react'
import { postAlert } from '@/lib/api'

const DISTRICTS = [
  'Colombo','Gampaha','Kalutara','Kandy','Matale','Nuwara Eliya',
  'Galle','Matara','Hambantota','Jaffna','Kilinochchi','Mannar',
  'Mullaitivu','Vavuniya','Trincomalee','Batticaloa','Ampara',
  'Badulla','Monaragala','Ratnapura','Kegalle','Kurunegala',
  'Puttalam','Anuradhapura','Polonnaruwa',
]

export default function AlertForm() {
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setStatus('loading')
    const data = new FormData(e.currentTarget)
    const email = data.get('email') as string
    const filters: Record<string, string> = {}
    for (const [key, value] of Array.from(data.entries())) {
      if (key !== 'email' && typeof value === 'string' && value.trim()) {
        filters[key] = value.trim()
      }
    }
    const ok = await postAlert(email, filters)
    setStatus(ok ? 'success' : 'error')
  }

  if (status === 'success') {
    return (
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-8 text-center">
        <svg className="w-12 h-12 text-emerald-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 className="text-lg font-semibold text-emerald-800 mb-1">Alert created!</h3>
        <p className="text-sm text-emerald-600">We&apos;ll email you when matching listings appear.</p>
        <button
          onClick={() => setStatus('idle')}
          className="mt-4 text-sm text-emerald-700 underline cursor-pointer"
        >
          Create another alert
        </button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
      <div className="px-6 py-4 bg-brand-primary">
        <h2 className="text-sm font-bold text-white uppercase tracking-widest">Create Alert</h2>
        <p className="text-xs text-slate-400 mt-0.5">Get emailed when new listings match your criteria</p>
      </div>

      <div className="p-6 space-y-5">
        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-xs font-semibold text-brand-muted uppercase tracking-wide mb-1.5">
            Email address <span className="text-brand-cta">*</span>
          </label>
          <input
            id="email"
            type="email"
            name="email"
            required
            placeholder="you@example.com"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-brand-cta"
          />
        </div>

        {/* Body type */}
        <div>
          <label htmlFor="body_type" className="block text-xs font-semibold text-brand-muted uppercase tracking-wide mb-1.5">
            Body type
          </label>
          <select
            id="body_type"
            name="body_type"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-brand-cta bg-white cursor-pointer"
          >
            <option value="">Any</option>
            <option value="4x4">4×4 / 4WD / AWD</option>
            <option value="double_cab">Double Cab Pickup</option>
            <option value="suv">SUV</option>
          </select>
        </div>

        {/* Price range */}
        <div>
          <p className="text-xs font-semibold text-brand-muted uppercase tracking-wide mb-1.5">Price range (LKR)</p>
          <div className="grid grid-cols-2 gap-3">
            <input type="number" name="price_min" placeholder="Min" min={0}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-brand-cta" />
            <input type="number" name="price_max" placeholder="Max" min={0}
              className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-brand-cta" />
          </div>
        </div>

        {/* District */}
        <div>
          <label htmlFor="alert_district" className="block text-xs font-semibold text-brand-muted uppercase tracking-wide mb-1.5">
            District
          </label>
          <select
            id="alert_district"
            name="district"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-brand-cta bg-white cursor-pointer"
          >
            <option value="">All districts</option>
            {DISTRICTS.map((d) => (
              <option key={d} value={d.toLowerCase()}>{d}</option>
            ))}
          </select>
        </div>

        {/* Fuel type */}
        <div>
          <label htmlFor="fuel_type" className="block text-xs font-semibold text-brand-muted uppercase tracking-wide mb-1.5">
            Fuel type
          </label>
          <select
            id="fuel_type"
            name="fuel_type"
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-brand-cta bg-white cursor-pointer"
          >
            <option value="">Any</option>
            <option value="petrol">Petrol</option>
            <option value="diesel">Diesel</option>
            <option value="hybrid">Hybrid</option>
          </select>
        </div>

        {status === 'error' && (
          <p className="text-sm text-brand-cta bg-red-50 border border-red-200 rounded-lg px-3 py-2">
            Failed to create alert. Please check the API is running and try again.
          </p>
        )}

        <button
          type="submit"
          disabled={status === 'loading'}
          className="w-full py-2.5 bg-brand-cta text-white text-sm font-bold uppercase tracking-widest rounded-lg hover:bg-red-700 disabled:opacity-60 transition-colors duration-200 cursor-pointer"
        >
          {status === 'loading' ? 'Creating…' : 'Create Alert'}
        </button>
      </div>
    </form>
  )
}
