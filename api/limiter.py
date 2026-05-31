from fastapi import Request
from slowapi import Limiter


def _real_ip(request: Request) -> str:
    # Cloudflare sets CF-Connecting-IP to the original client IP.
    # Fall back to direct peer address when running without Cloudflare.
    return (
        request.headers.get("CF-Connecting-IP")
        or (request.client.host if request.client else "unknown")
    )


limiter = Limiter(key_func=_real_ip)
