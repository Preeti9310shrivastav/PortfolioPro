"""
Standardized API Exception Handler for PortfolioPro.
Ensures all API responses adhere to the standard JSON envelope:
{
    "status": "error",
    "message": "Human readable error summary",
    "errors": { "field": ["detail", ...] }
}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first to get standard response
    response = exception_handler(exc, context)

    if response is not None:
        custom_errors = {}
        message = "An error occurred while processing your request."

        # Format details into consistent dictionary
        if isinstance(response.data, dict):
            for field, details in response.data.items():
                if field == 'detail':
                    message = str(details)
                    custom_errors['detail'] = [str(details)]
                elif isinstance(details, list):
                    custom_errors[field] = [str(d) for d in details]
                elif isinstance(details, dict):
                    custom_errors[field] = details
                else:
                    custom_errors[field] = [str(details)]
            if 'detail' in response.data and len(response.data) > 1:
                custom_errors.pop('detail', None)
        elif isinstance(response.data, list):
            custom_errors['non_field_errors'] = [str(d) for d in response.data]
            message = str(response.data[0]) if response.data else message
        else:
            custom_errors['detail'] = [str(response.data)]
            message = str(response.data)

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            if 'detail' not in custom_errors or len(custom_errors) > 1:
                message = "Validation error. Please verify the submitted data."
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            message = message if message != "An error occurred while processing your request." else "Authentication credentials were not provided or are invalid."
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            message = "Access forbidden. You do not have permission to perform this action."
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            message = message if message != "An error occurred while processing your request." else "The requested resource was not found."

        response.data = {
            "status": "error",
            "message": message,
            "errors": custom_errors
        }
    else:
        # Unhandled server errors (500)
        logger.error(f"Unhandled server exception: {exc}", exc_info=True)
        response = Response(
            {
                "status": "error",
                "message": "Internal server error. Our engineering team has been notified.",
                "errors": {
                    "server": ["An unexpected error occurred."]
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
