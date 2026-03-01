from deltadaemon.errors import (
    APIError,
    AuthenticationError,
    DeltaDaemonError,
    PaymentRequiredError,
    RateLimitError,
    RequestTimeoutError,
    TransportError,
    ValidationError,
)


def test_error_hierarchy() -> None:
    assert issubclass(AuthenticationError, APIError)
    assert issubclass(AuthenticationError, DeltaDaemonError)
    assert issubclass(PaymentRequiredError, APIError)
    assert issubclass(RateLimitError, APIError)
    assert issubclass(RequestTimeoutError, APIError)
    assert issubclass(TransportError, DeltaDaemonError)
    assert issubclass(ValidationError, DeltaDaemonError)


def test_authentication_error_attributes() -> None:
    err = AuthenticationError("Invalid credentials", status_code=401)
    assert err.message == "Invalid credentials"
    assert err.status_code == 401


def test_api_error_message() -> None:
    err = APIError("Server error", status_code=500)
    assert str(err) == "Server error"
