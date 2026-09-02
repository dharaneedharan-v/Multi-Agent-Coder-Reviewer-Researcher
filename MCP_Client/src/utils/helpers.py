
from src.models.models import APIResponse
def success_response(message: str, data=None, code: int = 200):

    return APIResponse(
        code=code,
        status="success",
        message=message,
        data=data,
        error=None
    )


def error_response(message: str, error=None, code: int = 500):
    return APIResponse(
        code=code,
        status="error",
        message=message,
        data=None,
        error={"details": str(error)} if error else None
    )


