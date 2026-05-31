"""
Seed Firestore with realistic test listings to verify the full API/frontend stack.

Usage:
    # Against real Firestore (needs service-account.json or GOOGLE_APPLICATION_CREDENTIALS_JSON):
    python seed_firestore.py

    # Against local Firebase Emulator:
    FIRESTORE_EMULATOR_HOST=localhost:8080 GOOGLE_CLOUD_PROJECT=demo-70sl python seed_firestore.py

    # Wipe all seeded docs and exit:
    python seed_firestore.py --wipe
"""
import argparse
import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

from db.firestore_client import get_db
from scraper.pipeline.dedup import doc_id_from_url, upsert_listing

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

_SEED_LISTINGS = [
    {
        "source": "ikman",
        "source_url": "https://ikman.lk/en/ad/toyota-hilux-double-cab-2019-seed-1",
        "title": "Toyota Hilux Double Cab 2019 - Low Mileage",
        "body_type": "double_cab",
        "make": "toyota",
        "model": "hilux",
        "year": 2019,
        "price_lkr": 18500000,
        "mileage_km": 62000,
        "fuel_type": "diesel",
        "transmission": "automatic",
        "district": "colombo",
        "description": "Well-maintained Hilux Double Cab. Single owner, full service history.",
        "image_urls": [
            "https://placehold.co/600x400?text=Hilux+Double+Cab"
        ],
    },
    {
        "source": "riyasewana",
        "source_url": "https://riyasewana.com/buy/toyota-land-cruiser-prado-2017-seed-2",
        "title": "Toyota Land Cruiser Prado 4x4 2017",
        "body_type": "4x4",
        "make": "toyota",
        "model": "land cruiser prado",
        "year": 2017,
        "price_lkr": 29800000,
        "mileage_km": 88000,
        "fuel_type": "diesel",
        "transmission": "automatic",
        "district": "kandy",
        "description": "Prado VX in excellent condition. Sun roof, leather seats, rear camera.",
        "image_urls": [
            "https://placehold.co/600x400?text=Prado+4x4"
        ],
    },
    {
        "source": "sarathiads",
        "source_url": "https://www.sarathiads.lk/vehicles/cars/mitsubishi-montero-2015-seed-3",
        "title": "Mitsubishi Montero Sport 4WD 2015",
        "body_type": "4x4",
        "make": "mitsubishi",
        "model": "montero sport",
        "year": 2015,
        "price_lkr": 14200000,
        "mileage_km": 130000,
        "fuel_type": "diesel",
        "transmission": "automatic",
        "district": "gampaha",
        "description": "Good condition. New tyres. All papers clear.",
        "image_urls": [
            "https://placehold.co/600x400?text=Montero+Sport"
        ],
    },
    {
        "source": "ikman",
        "source_url": "https://ikman.lk/en/ad/ford-ranger-double-cab-2020-seed-4",
        "title": "Ford Ranger Double Cab Wildtrak 2020",
        "body_type": "double_cab",
        "make": "ford",
        "model": "ranger",
        "year": 2020,
        "price_lkr": 22000000,
        "mileage_km": 41000,
        "fuel_type": "diesel",
        "transmission": "automatic",
        "district": "galle",
        "description": "Ford Ranger Wildtrak. Bi-xenon headlights. Tow bar. Very clean.",
        "image_urls": [
            "https://placehold.co/600x400?text=Ford+Ranger"
        ],
    },
    {
        "source": "riyasewana",
        "source_url": "https://riyasewana.com/buy/toyota-fortuner-suv-2018-seed-5",
        "title": "Toyota Fortuner SUV 2018 - Colombo",
        "body_type": "suv",
        "make": "toyota",
        "model": "fortuner",
        "year": 2018,
        "price_lkr": 21500000,
        "mileage_km": 74000,
        "fuel_type": "diesel",
        "transmission": "automatic",
        "district": "colombo",
        "description": "Fortuner in showroom condition. Original paint. All accessories.",
        "image_urls": [
            "https://placehold.co/600x400?text=Fortuner+SUV"
        ],
    },
    {
        "source": "ikman",
        "source_url": "https://ikman.lk/en/ad/isuzu-d-max-double-cab-2016-seed-6",
        "title": "Isuzu D-Max Double Cab 4WD 2016",
        "body_type": "double_cab",
        "make": "isuzu",
        "model": "d-max",
        "year": 2016,
        "price_lkr": 11900000,
        "mileage_km": 155000,
        "fuel_type": "diesel",
        "transmission": "manual",
        "district": "kurunegala",
        "description": "D-Max 4WD in good working order. Canopy included.",
        "image_urls": [
            "https://placehold.co/600x400?text=Isuzu+D-Max"
        ],
    },
    {
        "source": "sarathiads",
        "source_url": "https://www.sarathiads.lk/vehicles/cars/nissan-navara-2021-seed-7",
        "title": "Nissan Navara Double Cab 2021 - Negotiable",
        "body_type": "double_cab",
        "make": "nissan",
        "model": "navara",
        "year": 2021,
        "price_lkr": None,
        "mileage_km": 28000,
        "fuel_type": "diesel",
        "transmission": "automatic",
        "district": "matara",
        "description": "Navara Pro-4X. Price negotiable for serious buyers.",
        "image_urls": [
            "https://placehold.co/600x400?text=Nissan+Navara"
        ],
    },
    {
        "source": "riyasewana",
        "source_url": "https://riyasewana.com/buy/jeep-wrangler-4x4-2014-seed-8",
        "title": "Jeep Wrangler 4x4 Sahara 2014",
        "body_type": "4x4",
        "make": "jeep",
        "model": "wrangler",
        "year": 2014,
        "price_lkr": 17800000,
        "mileage_km": 98000,
        "fuel_type": "petrol",
        "transmission": "automatic",
        "district": "colombo",
        "description": "Hard top Wrangler Sahara. Lift kit installed. Rock rails.",
        "image_urls": [
            "https://placehold.co/600x400?text=Jeep+Wrangler"
        ],
    },
]


async def seed(wipe: bool = False) -> None:
    db = get_db()

    if wipe:
        log.info("Wiping seeded documents...")
        for listing in _SEED_LISTINGS:
            doc_id = doc_id_from_url(listing["source_url"])
            await db.collection("listings").document(doc_id).delete()
            log.info("Deleted %s", doc_id)
        log.info("Done — %d documents deleted.", len(_SEED_LISTINGS))
        return

    log.info("Seeding %d listings...", len(_SEED_LISTINGS))
    for listing in _SEED_LISTINGS:
        status = await upsert_listing(db, listing)
        log.info("[%s] %s", status, listing["title"])

    log.info("Done. Open /listings in the API or frontend to verify.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed Firestore with test listings")
    parser.add_argument("--wipe", action="store_true", help="Delete all seeded docs")
    args = parser.parse_args()
    asyncio.run(seed(wipe=args.wipe))
