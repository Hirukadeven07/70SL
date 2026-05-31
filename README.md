<div align="center">

<!-- Place your banner image at assets/banner.png -->
<img src="assets/banner.png" alt="70SL Banner" width="100%" />
<br/>

[![Website](https://img.shields.io/badge/Live-70sl.up.railway.app-blue?style=flat-square)](https://70sl.up.railway.app/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square)](https://www.python.org/downloads/release/python-3120/)
[![Stars](https://img.shields.io/github/stars/Hirukadeven07/70SL?style=flat-square)](https://github.com/Hirukadeven07/70SL/stargazers)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=flat-square)](https://nextjs.org/)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-orange?style=flat-square)](https://firebase.google.com/)

</div>

---

**A full-stack scraper and search platform for 4x4 SUV and double-cab pickup truck listings in Sri Lanka.**

Aggregates vehicle listings from [ikman.lk](https://www.ikman.lk), [riyasewana.com](https://riyasewana.com), and [sarathiads.lk](https://www.sarathiads.lk) using Playwright-powered scrapers running on Cloud Run Jobs. Scraped data is normalised, deduplicated, and stored in Firestore — then served via a FastAPI backend and displayed in a Next.js frontend with filtering, map view, and a watchlist/alerts system.

---

## Architecture

```
Cloud Run Jobs          →  Firestore  →  FastAPI (Cloud Run)  →  Next.js
(Playwright scrapers)      Firebase                               (Firebase Hosting)
Cloud Scheduler (cron)     Storage
```

Firebase Hosting proxies `/api/**` to the FastAPI Cloud Run service.

---

## Features

- Scrapes 4x4 SUVs and double-cab pickups from three Sri Lankan listing sites
- Deduplication via URL-based document IDs and SHA-256 content hashing
- Price, mileage, and year normalisation pipeline
- Filtering by body type, make, model, year range, price range, district, and fuel type
- Map view using Leaflet.js with district-level coordinates
- Similar listings endpoint
- Rate-limited FastAPI with slowapi (per Cloud Run instance)
- ISR-cached Next.js frontend (1-minute revalidation)

---

## Stack

| Layer     | Technology                                         |
|-----------|----------------------------------------------------|
| Scraper   | Python 3.12, Playwright, Cloud Run Jobs            |
| Schedule  | Cloud Scheduler                                    |
| DB        | Firestore (firebase-admin + google-cloud-firestore) |
| API       | FastAPI 0.111, Pydantic v2, slowapi               |
| Frontend  | Next.js 14 (App Router), Tailwind CSS 3            |
| Storage   | Firebase Storage                                   |
| Hosting   | Firebase Hosting + Cloud Run                       |

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose
- Firebase CLI (`npm install -g firebase-tools`)
- A Firebase project with Firestore enabled

### Local development

```bash
# 1. Clone the repo
git clone https://github.com/Hirukadeven07/70SL.git
cd 70SL

# 2. Copy env template and fill in your values
cp .env.example .env

# 3. Start Firebase Emulator + API
docker-compose up -d

# 4. Start the frontend
cd frontend && npm install && npm run dev

# 5. Run a scraper manually against the emulator
FIRESTORE_EMULATOR_HOST=localhost:8080 \
FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199 \
GOOGLE_CLOUD_PROJECT=demo-70sl \
python -m scraper.main --source ikman
```

The API will be available at `http://localhost:8000` and the frontend at `http://localhost:3000`.

---

## Environment Variables

```ini
# Google Cloud / Firebase
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
GOOGLE_CLOUD_PROJECT=your-firebase-project-id
FIREBASE_STORAGE_BUCKET=your-firebase-project-id.appspot.com

# API server
PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Local dev (Firebase Emulator)
# FIRESTORE_EMULATOR_HOST=localhost:8080
# FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/listings` | List & filter listings (body_type, make, model, year, price, district, fuel_type, sort, page) |
| `GET` | `/listings/{id}` | Single listing by ID |
| `GET` | `/listings/{id}/similar` | Similar listings |
| `POST` | `/alerts` | Create a watchlist alert |
| `DELETE` | `/alerts/{id}` | Delete an alert |
| `GET` | `/health` | Health check |

---

## Deployment

```bash
# Deploy frontend to Firebase Hosting
firebase deploy --only hosting

# Deploy API to Cloud Run
gcloud run deploy 70sl-api \
  --source . \
  --dockerfile api/Dockerfile \
  --region us-central1

# Create scraper Cloud Run Job
gcloud run jobs create scraper-ikman \
  --image gcr.io/PROJECT_ID/70sl-scraper \
  --args="--source,ikman" \
  --region us-central1
```

---

## Project Structure

```
70SL/
├── scraper/workers/        # Playwright scrapers (ikman, riyasewana, sarathiads)
├── scraper/pipeline/       # Dedup, normalise, image store
├── api/                    # FastAPI app + routers
├── db/                     # Pydantic models + Firestore client
├── frontend/               # Next.js app (App Router)
├── infra/                  # Cloud Scheduler job definitions
├── assets/                 # Banner and static assets
└── docker-compose.yml      # Local dev (Firebase Emulator + API)
```

---

## License

This project is licensed under the [MIT License](LICENSE).
