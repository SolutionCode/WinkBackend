from rest_framework.views import exception_handler as original_exception_handler
from rest_framework.exceptions import ValidationError


HTTP_422_UNPROCESSABLE_ENTITY = 422


def exception_handler(exc, context):
    response = original_exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        response.status_code = HTTP_422_UNPROCESSABLE_ENTITY
        response.data = {"errors": response.data}

    return response
