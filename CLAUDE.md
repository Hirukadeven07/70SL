# Sri Lanka 4x4 / Double-Cab Listings Scraper

## Project overview

Build a web scraper that finds 4x4 SUVs and double-cab pickup trucks listed for
sale in Sri Lanka. Scraped data is stored in Firestore, served via a FastAPI
backend on Cloud Run, and displayed in a Next.js frontend hosted on Firebase Hosting.

## Target sites

- https://www.ikman.lk/en/ads/sri-lanka/vehicles
- https://riyasewana.com/search/
- https://www.sarathiads.lk/

Scrape only public listing pages. Respect `robots.txt`. Add a minimum 2-second
delay between requests per domain. Never bypass login walls or CAPTCHAs.

---

## Architecture

```
Cloud Run Jobs          →  Firestore  →  FastAPI (Cloud Run)  →  Next.js
(Playwright scrapers)      Firebase                               (Firebase Hosting)
Cloud Scheduler (cron)     Storage
```

Firebase Hosting proxies `/api/**` to the FastAPI Cloud Run service.

---

## Stack & versions

| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Scraper   | Python 3.12, Playwright, Cloud Run Jobs         |
| Schedule  | Cloud Scheduler (replaces Celery Beat)          |
| DB        | Firestore (firebase-admin + google-cloud-firestore) |
| API       | FastAPI 0.111, Pydantic v2, slowapi             |
| Frontend  | Next.js 14 (App Router), Tailwind CSS 3         |
| Storage   | Firebase Storage (images)                       |
| Hosting   | Firebase Hosting (frontend) + Cloud Run (API)   |

---

## Repository structure

```
project-root/
├── CLAUDE.md
├── firebase.json              # Firebase Hosting + emulator config
├── .firebaserc                # Firebase project aliases
├── firestore.rules            # Firestore security rules
├── firestore.indexes.json     # Compound indexes for filter queries
├── storage.rules              # Firebase Storage security rules
├── scraper/
│   ├── workers/
│   │   ├── base.py            # BaseScraper class
│   │   ├── ikman.py
│   │   ├── riyasewana.py
│   │   └── sarathiads.py
│   ├── pipeline/
│   │   ├── dedup.py           # URL + content hash dedup (Firestore upsert)
│   │   ├── normalise.py       # price, mileage, year normalisation
│   │   └── image_store.py     # download & upload to Firebase Storage
│   ├── main.py                # Cloud Run Job entrypoint
│   └── Dockerfile
├── api/
│   ├── main.py
│   ├── routers/
│   │   ├── listings.py
│   │   └── alerts.py
│   ├── schemas.py             # Pydantic models
│   ├── db.py                  # Firestore client dependency
│   ├── limiter.py             # slowapi rate limiter
│   └── Dockerfile
├── db/
│   ├── models.py              # Pydantic data models (Listing, Alert)
│   └── firestore_client.py    # firebase-admin init + get_db()
├── frontend/                  # Next.js app
│   ├── app/
│   │   ├── page.tsx           # listing search page
│   │   └── alerts/page.tsx    # watchlist page
│   └── components/
│       ├── ListingCard.tsx
│       ├── FilterSidebar.tsx
│       └── MapView.tsx
├── infra/
│   └── cloud_scheduler.yaml   # Cloud Scheduler job definitions
├── docker-compose.yml         # Firebase Emulator + API for local dev
├── .env.example
└── pyproject.toml
```

---

## Firestore collections

### `listings` collection

Each document ID is `md5(source_url)`. Fields:

| Field         | Type      | Notes                                    |
|---------------|-----------|------------------------------------------|
| source        | string    | `'ikman'` \| `'riyasewana'` \| `'sarathiads'` |
| source_url    | string    | original listing URL                     |
| title         | string    |                                          |
| body_type     | string?   | `'4x4'` \| `'double_cab'` \| `'suv'`    |
| make          | string?   | lowercase                                |
| model         | string?   | lowercase                                |
| year          | integer?  |                                          |
| price_lkr     | integer?  | null if not listed                       |
| mileage_km    | integer?  |                                          |
| fuel_type     | string?   | `'petrol'` \| `'diesel'` \| `'hybrid'`  |
| transmission  | string?   | `'manual'` \| `'automatic'`             |
| district      | string?   | lowercase                                |
| description   | string?   |                                          |
| image_urls    | string[]  | Firebase Storage public URLs             |
| content_hash  | string    | SHA-256 of title+price+mileage           |
| scraped_at    | timestamp |                                          |
| updated_at    | timestamp |                                          |
| is_active     | boolean   |                                          |

### `alerts` collection

Document ID is a UUID string. Fields: `email`, `filters` (map), `created_at`.

---

## Scraper conventions

### BaseScraper interface

Every scraper must implement:

```python
class BaseScraper:
    source: str
    base_url: str

    async def fetch_listing_urls(self) -> list[str]: ...
    async def parse_listing(self, url: str, html: str) -> dict | None: ...
```

### Filtering rules

Only keep a listing if **at least one** is true:
- `body_type` resolves to `4x4`, `double_cab`, or `suv`
- Title contains (case-insensitive): `4x4`, `4wd`, `awd`, `double cab`,
  `double-cab`, `pickup`, `hilux`, `ranger`, `d-max`, `triton`, `navara`,
  `fortuner`, `prado`, `landcruiser`, `pajero`, `montero`, `surf`

### Dedup logic

`content_hash = sha256(title + str(price_lkr) + str(mileage_km))`

Document ID = `md5(source_url)`. On each scrape:
- Document absent → insert
- Document present, same hash → skip
- Document present, different hash → update + bump `updated_at`

### Rate limiting

```python
RATE_LIMITS = {
    "ikman":      {"delay_s": 3, "concurrency": 2},
    "riyasewana": {"delay_s": 4, "concurrency": 1},
    "sarathiads": {"delay_s": 3, "concurrency": 2},
}
```

---

## FastAPI conventions

- All routes are async.
- Firestore client injected via `Depends(get_firestore)`.
- Validate with Pydantic v2 models; never pass raw dicts across the API boundary.
- Return 404 with a clear message when a listing is not found.
- `slowapi` rate-limits all endpoints (in-memory; per Cloud Run instance).

### Key endpoints

```
GET  /listings          # filter: body_type, make, model, year_min, year_max,
                        #         price_min, price_max, district, fuel_type,
                        #         sort (price_asc|price_desc|newest)
                        # paginate: page, page_size (max 50)
GET  /listings/{id}
GET  /listings/{id}/similar
POST /alerts            # body: { email, filters }
DELETE /alerts/{id}
GET  /health
```

---

## Frontend conventions

- Use the Next.js App Router (`app/` directory).
- Fetch listings via `fetch()` with `{ next: { revalidate: 60 } }` (ISR, 1-min cache).
- `FilterSidebar` emits a `filters` object; the parent page updates the URL search
  params and re-fetches.
- `ListingCard` shows: thumbnail, title, price (LKR), year, mileage, district,
  source badge, and a "View original" link.
- `MapView` uses Leaflet.js with `district_centroids.json` for coordinates.
- Mobile-first; Tailwind `sm` and `md` breakpoints are sufficient.

---

## Environment variables

```ini
# Google Cloud / Firebase
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
GOOGLE_CLOUD_PROJECT=your-firebase-project-id
FIREBASE_STORAGE_BUCKET=your-firebase-project-id.appspot.com

# API server
PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Email alerts
ALERT_FROM_EMAIL=alerts@yourdomain.com

# Local dev (Firebase Emulator)
# FIRESTORE_EMULATOR_HOST=localhost:8080
# FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199
```

---

## Development workflow

```bash
# 1. Install Firebase CLI
npm install -g firebase-tools
firebase login

# 2. Start Firebase Emulator + API
docker-compose up -d

# 3. Start frontend
cd frontend && npm run dev

# 4. Run a scraper manually (against the emulator)
FIRESTORE_EMULATOR_HOST=localhost:8080 \
FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199 \
GOOGLE_CLOUD_PROJECT=demo-70sl \
python -m scraper.main --source ikman
```

### Deploying to Firebase / GCP

```bash
# Deploy frontend to Firebase Hosting
firebase deploy --only hosting

# Build and push API image to Cloud Run
gcloud run deploy 70sl-api \
  --source . \
  --dockerfile api/Dockerfile \
  --region us-central1

# Build and push scraper image as a Cloud Run Job
gcloud run jobs create scraper-ikman \
  --image gcr.io/PROJECT_ID/70sl-scraper \
  --args="--source,ikman" \
  --region us-central1
```

---

## Code style

- Python: Black formatter, Ruff linter, type hints on every function signature.
- TypeScript: strict mode, no `any`, Prettier formatter.
- Commits: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`).
- Tests: pytest for Python (async with `pytest-asyncio`), Vitest for TS.
  Write a test for every scraper's `parse_listing` using a saved HTML fixture.

---

## What to build next (MVP order)

1. ~~`db/models.py` + Firestore client~~ ✓
2. ~~`scraper/workers/base.py` + `scraper/workers/ikman.py`~~ ✓
3. ~~`scraper/pipeline/dedup.py` + `scraper/pipeline/normalise.py`~~ ✓
4. ~~`api/` listings router with filtering & pagination~~ ✓
5. Remaining scrapers (`riyasewana.py`, `sarathiads.py`)
6. Alerts email dispatch
7. MapView + Similar listings endpoint

---

## Gotchas & known issues

- **ikman.lk** paginates via `?page=N`; stop when a page returns 0 listings.
- **riyasewana.com** lazy-loads images; use `page.wait_for_selector('.listing-img')`.
- **Price** appears as "Rs. 12,500,000" — strip `Rs.`, commas, and whitespace.
- **Mileage** sometimes says "100,000 km" or "100k km" — normalise both forms.
- **District** is inconsistently capitalised across sources — store lowercase.
- Listings without a price should still be stored; set `price_lkr = None`.
- **Firestore inequality ordering**: if you filter on `price_lkr` with a range,
  Firestore requires `order_by("price_lkr")`. Composite indexes in
  `firestore.indexes.json` cover the common filter+sort combinations.
- **Firestore count aggregation** requires `google-cloud-firestore >= 2.14`.
