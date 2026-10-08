"""One error envelope for every failure (docs/development/api-conventions.md).

    {"error": {"code": "...", "message": "...", "details": [...], "requestId": "..."}}

`exception_handler` covers DRF views. The Django handlers (`bad_request`, `not_found`, ...)
cover everything else, such as unknown URLs and errors outside DRF.
"""

from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.db import transaction
from django.http import Http404, HttpRequest, JsonResponse
from rest_framework import exceptions, status
from rest_framework.response import Response

from kayaka.core.context import get_request_id

GENERIC_MESSAGES = {
    "VALIDATION_ERROR": "Some fields need attention.",
    "BAD_REQUEST": "The request could not be understood.",
    "NOT_AUTHENTICATED": "Please sign in to continue.",
    "PERMISSION_DENIED": "You don't have permission to do that.",
    "CSRF_FAILED": "Your session token is missing or invalid. Refresh the page and try again.",
    "NOT_FOUND": "Not found.",
    "RATE_LIMITED": "Too many requests. Please wait and try again.",
    "INTERNAL_ERROR": "Something went wrong on our side. Please try again.",
}


def error_body(
    code: str,
    message: str | None = None,
    details: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "code": code,
        "message": message or GENERIC_MESSAGES.get(code, code.replace("_", " ").capitalize()),
        "requestId": get_request_id(),
    }
    if details:
        body["details"] = details
    return {"error": body}


def flatten_validation_detail(detail: Any, field: str | None = None) -> list[dict[str, Any]]:
    """Turn DRF's nested ValidationError detail into a flat list of {field, code, message}.

    Nested fields use dotted paths and list indexes, e.g. `variants[0].price`.
    """
    if isinstance(detail, dict):
        items: list[dict[str, Any]] = []
        for key, value in detail.items():
            child = field if key == "non_field_errors" else _join_field(field, str(key))
            items.extend(flatten_validation_detail(value, child))
        return items
    if isinstance(detail, list):
        if all(isinstance(item, str) for item in detail):  # ErrorDetail subclasses str
            return [_detail_item(field, item) for item in detail]
        items = []
        for index, value in enumerate(detail):
            items.extend(flatten_validation_detail(value, f"{field or ''}[{index}]"))
        return items
    return [_detail_item(field, detail)]


def _join_field(parent: str | None, key: str) -> str:
    return f"{parent}.{key}" if parent else key


def _detail_item(field: str | None, item: Any) -> dict[str, Any]:
    return {"field": field, "code": getattr(item, "code", "invalid"), "message": str(item)}


def _code_for(exc: exceptions.APIException) -> str:
    if isinstance(exc, exceptions.ValidationError):
        return "VALIDATION_ERROR"
    if isinstance(exc, exceptions.ParseError):
        return "BAD_REQUEST"
    if isinstance(exc, exceptions.NotAuthenticated | exceptions.AuthenticationFailed):
        return "NOT_AUTHENTICATED"
    if isinstance(exc, exceptions.Throttled):
        return "RATE_LIMITED"
    if isinstance(exc, exceptions.PermissionDenied) and str(exc.detail).startswith("CSRF Failed"):
        return "CSRF_FAILED"
    codes = exc.get_codes()
    code = codes if isinstance(codes, str) else exc.default_code
    return str(code).upper()


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """DRF exception handler. Non-API exceptions return None so Django logs them and answers 500."""
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    if not isinstance(exc, exceptions.APIException):
        return None

    code = _code_for(exc)
    headers: dict[str, str] = {}
    status_code = exc.status_code
    details = None
    message: str | None = None

    if code == "VALIDATION_ERROR":
        details = flatten_validation_detail(exc.detail)
    elif code == "NOT_AUTHENTICATED":
        # DRF downgrades to 403 when no WWW-Authenticate scheme exists (session auth). Our
        # contract is 401 for "not signed in" and 403 for "signed in but not allowed".
        status_code = status.HTTP_401_UNAUTHORIZED
    elif code == "RATE_LIMITED":
        wait = getattr(exc, "wait", None)  # DRF already rounds up to whole seconds
        if wait is not None:
            headers["Retry-After"] = str(int(wait))
    elif code not in GENERIC_MESSAGES and isinstance(exc.detail, str):
        message = str(exc.detail)

    return Response(error_body(code, message, details), status=status_code, headers=headers)


# ---------------------------------------------------------------- Django-level handlers


def _json_error(code: str, status_code: int) -> JsonResponse:
    return JsonResponse(error_body(code), status=status_code)


def bad_request(request: HttpRequest, exception: Exception | None = None) -> JsonResponse:
    return _json_error("BAD_REQUEST", 400)


def permission_denied(request: HttpRequest, exception: Exception | None = None) -> JsonResponse:
    return _json_error("PERMISSION_DENIED", 403)


def not_found(request: HttpRequest, exception: Exception | None = None) -> JsonResponse:
    return _json_error("NOT_FOUND", 404)


@transaction.non_atomic_requests
def api_not_found(request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
    """Catch-all for unknown /api/v1/ URLs. Unlike handler404, this also applies with DEBUG=True,
    so API clients get the JSON envelope in every environment."""
    return _json_error("NOT_FOUND", 404)


def server_error(request: HttpRequest) -> JsonResponse:
    return _json_error("INTERNAL_ERROR", 500)


def csrf_failure(request: HttpRequest, reason: str = "") -> JsonResponse:
    return _json_error("CSRF_FAILED", 403)
