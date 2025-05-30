import logging
from logging import Filter
from .request_context import get_request_context


class ClientIPFilter(Filter):
    """Add the client IP to the log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add the client IP to the log records.

        First tries to get the original client IP from X-Forwarded-For header (for Docker/proxy environments)
        If not available, falls back to request.client.host
        If no request context is available, uses '127.0.0.1' as the default IP
        """
        request = get_request_context()
        if request:
            # Try to get the original client IP from X-Forwarded-For header
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                # Take the first IP from the comma-separated list
                record.client_ip = forwarded_for.split(",")[0].strip()
            elif hasattr(request, "client"):
                record.client_ip = request.client.host
        else:
            # If no request context is available, use '127.0.0.1' IP
            record.client_ip = "127.0.0.1"
        return True
