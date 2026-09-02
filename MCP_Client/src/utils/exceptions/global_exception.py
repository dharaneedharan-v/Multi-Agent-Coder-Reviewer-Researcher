# from fastapi import Request
# from fastapi.responses import JSONResponse
# from src.utils.exceptions.custom_exception import AppException
# from src.utils.logger.log import *
# logger = get_logger(__name__)


# def global_register_exception_handlers(app):
#     """
#     Registers global exception handlers for the FastAPI application.

#     This function attaches a handler for `AppException` so that whenever
#     such an exception is raised anywhere in the application, it is caught
#     and returned as a standardized JSON error response.

#     Parameters
#     ----------
#     app : FastAPI
#         The FastAPI application instance to which the exception handler
#         will be registered.

#     Returns
#     -------
#     None
#         This function modifies the `app` instance in place.  
#     """
#     @app.exception_handler(AppException)
#     async def app_exception_handler(request: Request, exc: AppException):
#         return JSONResponse(
#             status_code=exc.status_code,
#             content={
#                 "code": exc.error_code,
#                 "message": exc.message,
#                 "status": "error"
#             },
#         )




from fastapi import Request
from fastapi.responses import JSONResponse
from src.utils.exceptions.custom_exception import AppException
from src.utils.logger.log import *
from src.models.models import APIResponse
from fastapi.exceptions import RequestValidationError

logger = get_logger(__name__)


def global_register_exception_handlers(app):

    # -----------------------------
    # Custom App Exception
    # -----------------------------
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):

        logger.error(f"AppException: {exc.message}")

        response = APIResponse(
            code=exc.status_code,
            status="error",
            message=exc.message,
            data=None,
            error={
                "error_code": exc.error_code,
                "details": exc.message
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=response.dict()
        )

    # -----------------------------
    # Global Exception
    # -----------------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):

        logger.exception("Unhandled Exception occurred")

        response = APIResponse(
            code=500,
            status="error",
            message="Internal Server Error",
            data=None,
            error={
                "details": str(exc)
            }
        )

        return JSONResponse(
            status_code=500,
            content=response.dict()
        )
    

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):

        logger.error(f"Validation Error: {exc.errors()}")

        # Format errors cleanly
        formatted_errors = []

        for err in exc.errors():

            field = ".".join(map(str, err.get("loc", [])))

            formatted_errors.append({
                "field": field,
                "message": err.get("msg")
            })

        response = APIResponse(
            code=422,
            status="error",
            message="Validation Error",
            data=None,
            error={
                "fields": formatted_errors
            }
        )

        return JSONResponse(
            status_code=422,
            content=response.dict()
        )