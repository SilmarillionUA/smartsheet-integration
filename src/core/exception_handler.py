import logging

from django.core.exceptions import ObjectDoesNotExist

import smartsheet.exceptions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, ObjectDoesNotExist):
        return Response(
            {"error": "Not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if isinstance(exc, ValueError):
        return Response(
            {"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST
        )

    if isinstance(exc, smartsheet.exceptions.RateLimitExceededError):
        logger.warning("Smartsheet rate limit exceeded")
        return Response(
            {
                "error": "Smartsheet rate limit exceeded. Please try again shortly."  # noqa: E501
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    if isinstance(exc, smartsheet.exceptions.SystemMaintenanceError):
        logger.warning("Smartsheet under maintenance")
        return Response(
            {
                "error": "Smartsheet is currently under maintenance. Please try again later."  # noqa: E501
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    if isinstance(exc, smartsheet.exceptions.ServerTimeoutExceededError):
        logger.warning("Smartsheet request timed out")
        return Response(
            {"error": "Smartsheet request timed out. Please try again."},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )

    if isinstance(exc, smartsheet.exceptions.ApiError):
        message = getattr(exc, "message", None) or "Smartsheet API error"
        logger.error("Smartsheet API error: %s", message)
        return Response(
            {"error": message},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if isinstance(
        exc,
        (
            smartsheet.exceptions.HttpError,
            smartsheet.exceptions.UnexpectedRequestError,
        ),
    ):
        logger.error("Smartsheet connection error: %s", exc)
        return Response(
            {"error": "Failed to communicate with Smartsheet."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return None
