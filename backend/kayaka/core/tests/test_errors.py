import json

import pytest
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from django.test import RequestFactory
from rest_framework import exceptions, status

from kayaka.core.api.errors import exception_handler, flatten_validation_detail, server_error
from kayaka.core.context import reset_request_id, set_request_id


@pytest.fixture
def request_id():
    token = set_request_id("req_test_123456")
    yield "req_test_123456"
    reset_request_id(token)


def handle(exc):
    return exception_handler(exc, {})


def test_unknown_api_url_returns_not_found_envelope(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert error["requestId"] == response["X-Request-ID"]


def test_validation_error_is_flattened(request_id):
    exc = exceptions.ValidationError(
        {
            "email": ["Enter a valid email address."],
            "variants": [{}, {"price": [exceptions.ErrorDetail("Too low.", code="min_value")]}],
            "non_field_errors": ["Passwords do not match."],
        }
    )
    response = handle(exc)
    assert response.status_code == 400
    error = response.data["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["requestId"] == request_id
    assert {"field": "email", "code": "invalid", "message": "Enter a valid email address."} in (
        error["details"]
    )
    assert {"field": "variants[1].price", "code": "min_value", "message": "Too low."} in (
        error["details"]
    )
    assert {"field": None, "code": "invalid", "message": "Passwords do not match."} in (
        error["details"]
    )


def test_flatten_plain_list_detail():
    assert flatten_validation_detail(["Bad."]) == [
        {"field": None, "code": "invalid", "message": "Bad."}
    ]


@pytest.mark.parametrize(
    "exc",
    [exceptions.NotAuthenticated(), exceptions.AuthenticationFailed()],
)
def test_not_authenticated_is_401(exc):
    exc.status_code = status.HTTP_403_FORBIDDEN  # what DRF does for session auth
    response = handle(exc)
    assert response.status_code == 401
    assert response.data["error"]["code"] == "NOT_AUTHENTICATED"


def test_throttled_sets_retry_after():
    response = handle(exceptions.Throttled(wait=12.4))
    assert response.status_code == 429
    assert response.data["error"]["code"] == "RATE_LIMITED"
    assert response["Retry-After"] == "13"


def test_csrf_failure_is_distinguished():
    response = handle(exceptions.PermissionDenied("CSRF Failed: CSRF token missing."))
    assert response.status_code == 403
    assert response.data["error"]["code"] == "CSRF_FAILED"


def test_permission_denied_uses_generic_message():
    response = handle(exceptions.PermissionDenied("internal reason"))
    assert response.data["error"]["code"] == "PERMISSION_DENIED"
    assert "internal reason" not in response.data["error"]["message"]


def test_django_exceptions_are_translated():
    assert handle(Http404()).data["error"]["code"] == "NOT_FOUND"
    assert handle(DjangoPermissionDenied()).data["error"]["code"] == "PERMISSION_DENIED"


def test_domain_error_code_comes_from_default_code():
    class ProductNotActive(exceptions.APIException):
        status_code = 409
        default_code = "product_not_active"
        default_detail = "This product is no longer available."

    response = handle(ProductNotActive())
    assert response.status_code == 409
    assert response.data["error"] == {
        "code": "PRODUCT_NOT_ACTIVE",
        "message": "This product is no longer available.",
        "requestId": None,
    }


def test_unexpected_exceptions_are_left_to_django():
    assert handle(RuntimeError("boom")) is None


def test_server_error_handler_hides_internals(request_id):
    response = server_error(RequestFactory().get("/"))
    assert response.status_code == 500
    assert json.loads(response.content) == {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "Something went wrong on our side. Please try again.",
            "requestId": request_id,
        }
    }
