from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory, per-process store. Fine for a single Uvicorn worker; if this ever runs with
# multiple workers/replicas, each gets its own counter, so the effective limit multiplies
# by worker count. Move to a Redis-backed storage_uri (settings.redis_url) if that matters.
limiter = Limiter(key_func=get_remote_address)
