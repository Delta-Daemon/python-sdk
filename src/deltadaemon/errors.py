class DeltaDaemonError(Exception):
    """Base exception for all DeltaDaemon SDK errors."""

    def __init__(self, message: str, *, request_id: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.request_id = request_id


class APIError(DeltaDaemonError):
    """API returned an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error_code: str | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message, request_id=request_id)
        self.status_code = status_code
        self.error_code = error_code


class AuthenticationError(APIError):
    """Authentication failed (401)."""


class PaymentRequiredError(APIError):
    """Subscription past due or cancelled (402)."""


class RateLimitError(APIError):
    """Rate limit exceeded."""


class RequestTimeoutError(APIError):
    """Request timed out."""


class ValidationError(DeltaDaemonError):
    """Invalid request parameters or response data."""


class TransportError(DeltaDaemonError):
    """Network or transport layer error."""
