import type { ListingFilters, PaginatedResponse } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export async function fetchListings(
  filters: ListingFilters
): Promise<PaginatedResponse | null> {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') params.set(key, String(value))
  }

  try {
    const res = await fetch(`${API_URL}/listings?${params.toString()}`, {
      next: { revalidate: 60 },
    })
    if (!res.ok) return null
    return (await res.json()) as PaginatedResponse
  } catch {
    return null
  }
}
