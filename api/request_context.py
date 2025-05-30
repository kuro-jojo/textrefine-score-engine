from contextvars import ContextVar
from fastapi import Request

_request_ctx_var: ContextVar[Request] = ContextVar('request_ctx')

def set_request_context(request: Request):
    """
    Set the request context.

    This is used internally by the score engine to store the current request
    instance in the request context. This is useful for getting the request
    instance in a request-independent context.

    Args:
        request (Request): The current request instance.
    """
    _request_ctx_var.set(request)

def get_request_context() -> Request:
    """
    Get the request context.

    If the request context is not set, this function returns None.

    Returns:
        Request: The current request instance or None.
    """
    try:
        return _request_ctx_var.get()
    except LookupError:
        return None
