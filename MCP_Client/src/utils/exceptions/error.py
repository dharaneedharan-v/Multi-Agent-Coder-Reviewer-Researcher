
from src.utils.exceptions.custom_exception import AppException
from src.utils.exceptions.error_codes import ErrorCode


def invalid_uuid():
    """
    Creates and returns a standardized application exception for invalid UUID format.

    This helper function is typically used when validating input identifiers
    that must be in UUID format. It encapsulates the HTTP status code, error code,
    and a human-readable message into an `AppException` instance.

    Returns
    -------
    AppException
        An application-specific exception with:
            - HTTP status code: 400 (Bad Request)
            - Error code: ErrorCode.INVALID_UUID
            - Message: "Invalid UUID format"

    Notes
    -----
    - `AppException` is assumed to be a custom exception class that accepts
      `(status_code, error_code, message)` as parameters.
    - `ErrorCode.INVALID_UUID` should be a predefined constant in your error code enum.
    """
    
    return AppException(400, ErrorCode.INVALID_UUID, "Invalid UUID format")
