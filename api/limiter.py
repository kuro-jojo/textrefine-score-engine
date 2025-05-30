from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, enabled=True)

def get_limiter():
    """Get the limiter instance."""
    return limiter
