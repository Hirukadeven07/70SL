import re


def normalise_listing(raw: dict) -> dict:
    """Apply field-level normalisations in-place on a copy of the raw scraped dict."""
    out = dict(raw)

    for field in ("district", "make", "model"):
        if out.get(field):
            out[field] = out[field].strip().lower()

    if isinstance(out.get("price_lkr"), str):
        out["price_lkr"] = _parse_price(out["price_lkr"])

    if isinstance(out.get("mileage_km"), str):
        out["mileage_km"] = _parse_mileage(out["mileage_km"])

    return out


def _parse_price(raw: str) -> int | None:
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def _parse_mileage(raw: str) -> int | None:
    raw = raw.lower().replace(",", "")
    m = re.search(r"(\d+\.?\d*)\s*k", raw)
    if m:
        return int(float(m.group(1)) * 1000)
    m = re.search(r"(\d+)", raw)
    return int(m.group(1)) if m else None
