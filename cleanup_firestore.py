"""
Remove junk listings (parts, rentals, finance ads) from Firestore.

By default does a soft-delete (sets is_active=False). Use --hard to permanently
delete documents. Always run --dry-run first to preview what will be removed.

Usage:
    python cleanup_firestore.py --dry-run          # preview only
    python cleanup_firestore.py                    # soft-delete junk
    python cleanup_firestore.py --hard             # hard-delete junk
    python cleanup_firestore.py --hard --dry-run   # preview hard-delete
"""
import argparse
import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

from db.firestore_client import get_db
from scraper.workers.base import is_relevant_title

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

_BATCH_SIZE = 400  # Firestore batch limit is 500; leave headroom


async def cleanup(dry_run: bool, hard_delete: bool) -> None:
    db = get_db()
    action = "hard-delete" if hard_delete else "soft-delete"
    mode = f"DRY RUN ({action})" if dry_run else action.upper()
    log.info("Mode: %s", mode)

    total_scanned = 0
    total_junk = 0
    last_doc = None

    while True:
        q = db.collection("listings").limit(_BATCH_SIZE)
        if last_doc:
            q = q.start_after(last_doc)

        docs = await q.get()
        if not docs:
            break

        last_doc = docs[-1]
        total_scanned += len(docs)

        junk_docs = [
            d for d in docs
            if not is_relevant_title((d.to_dict() or {}).get("title", ""))
        ]
        total_junk += len(junk_docs)

        if junk_docs and not dry_run:
            batch = db.batch()
            for doc in junk_docs:
                title = (doc.to_dict() or {}).get("title", "")[:60]
                log.info("  [%s] %s", action, title)
                if hard_delete:
                    batch.delete(doc.reference)
                else:
                    batch.update(doc.reference, {"is_active": False})
            await batch.commit()
        elif junk_docs and dry_run:
            for doc in junk_docs:
                title = (doc.to_dict() or {}).get("title", "")[:60]
                log.info("  [would %s] %s", action, title)

        log.info("Progress: scanned %d, junk found %d", total_scanned, total_junk)

        if len(docs) < _BATCH_SIZE:
            break

    log.info("Done. Scanned %d docs, %s %d junk listings.", total_scanned, "would " + action if dry_run else action + "d", total_junk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean junk listings from Firestore")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--hard", action="store_true", help="Permanently delete instead of soft-delete")
    args = parser.parse_args()
    asyncio.run(cleanup(dry_run=args.dry_run, hard_delete=args.hard))
