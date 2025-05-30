import logging
from logging import Filter
from .request_context import get_request_context


class ClientIPFilter(Filter):
    """Add the client IP to the log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add the client IP to the log records.

        If the request context is available, use the client IP from the request.
        Otherwise, use 'unknown' as the default IP.
        """
        request = get_request_context()
        if request and hasattr(request, "client"):
            record.client_ip = request.client.host
        else:
            # If no request context is available, use 'unknown' IP
            record.client_ip = "unknown"
        return True
