"""
Standardized API Response Helpers for PortfolioPro.
"""
from rest_framework.response import Response
from rest_framework import status

def api_success(data=None, message="Operation completed successfully.", status_code=status.HTTP_200_OK):
    """
    Standard Success Envelope:
    {
        "status": "success",
        "message": "...",
        "data": { ... }
    }
    """
    return Response(
        {
            "status": "success",
            "message": message,
            "data": data if data is not None else {}
        },
        status=status_code
    )

def api_error(message="Operation failed.", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standard Error Envelope:
    {
        "status": "error",
        "message": "...",
        "errors": { ... }
    }
    """
    return Response(
        {
            "status": "error",
            "message": message,
            "errors": errors if errors is not None else {}
        },
        status=status_code
    )
