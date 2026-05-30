export type Source = 'ikman' | 'riyasewana' | 'sarathiads'
export type BodyType = '4x4' | 'double_cab' | 'suv'
export type FuelType = 'petrol' | 'diesel' | 'hybrid'
export type Transmission = 'manual' | 'automatic'
export type SortOption = 'price_asc' | 'price_desc' | 'newest'

export interface Listing {
  id: string
  source: Source
  source_url: string
  title: string
  body_type: BodyType | null
  make: string | null
  model: string | null
  year: number | null
  price_lkr: number | null
  mileage_km: number | null
  fuel_type: FuelType | null
  transmission: Transmission | null
  district: string | null
  description: string | null
  image_urls: string[]
  content_hash: string
  scraped_at: string
  updated_at: string
  is_active: boolean
}

export interface PaginatedResponse {
  items: Listing[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface ListingFilters {
  body_type?: string
  make?: string
  model?: string
  year_min?: string
  year_max?: string
  price_min?: string
  price_max?: string
  district?: string
  fuel_type?: string
  transmission?: string
  sort?: string
  page?: string
  page_size?: string
}

export interface DistrictCentroid {
  name: string
  lat: number
  lng: number
}
