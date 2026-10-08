"""Request-level middleware: request IDs, access logging, proxy trust, API security headers."""

import hmac
import ipaddress
import logging
import re
import time
import uuid
from collections.abc import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from kayaka.core.context import reset_request_id, set_request_id

logger = logging.getLogger("kayaka.request")

GetResponse = Callable[[HttpRequest], HttpResponse]

REQUEST_ID_HEADER = "X-Request-ID"
_VALID_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{8,128}$")


def new_request_id() -> str:
    return f"req_{uuid.uuid7().hex}"


def resolve_request_id(incoming: str | None) -> str:
    """Accept a well-formed incoming ID (from the proxy or client); otherwise generate one."""
    if incoming and _VALID_REQUEST_ID.fullmatch(incoming):
        return incoming
    return new_request_id()


class RequestContextMiddleware:
    """Assigns a request ID, exposes it in logs and the response, and writes one access log line."""

    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = resolve_request_id(request.headers.get(REQUEST_ID_HEADER))
        token = set_request_id(request_id)
        started = time.perf_counter()
        try:
            response = self.get_response(request)
            response[REQUEST_ID_HEADER] = request_id
            duration_ms = round((time.perf_counter() - started) * 1000, 1)
            logger.info(
                "%s %s -> %s (%.1f ms)",
                request.method,
                request.path,  # no query string: it may contain personal data
                response.status_code,
                duration_ms,
                extra={
                    "event": "request.completed",
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                    "client_ip": request.META.get("REMOTE_ADDR"),
                },
            )
            return response
        finally:
            reset_request_id(token)


class TrustedProxyMiddleware:
    """Use the client IP forwarded by our Next.js proxy, but only when it proves itself (ADR 0003).

    The proxy sends `X-Kayaka-Proxy: <PROXY_SHARED_SECRET>` and `X-Kayaka-Client-IP`. Requests
    without the correct secret (including anyone calling the API origin directly) keep the socket
    address. `X-Forwarded-For` is never trusted.
    """

    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if is_trusted_proxy_request(request):
            client_ip = _parse_ip(request.headers.get("X-Kayaka-Client-IP", ""))
            if client_ip:
                request.META["REMOTE_ADDR"] = client_ip
        return self.get_response(request)


def is_trusted_proxy_request(request: HttpRequest) -> bool:
    secret: str = settings.PROXY_SHARED_SECRET
    provided = request.headers.get("X-Kayaka-Proxy", "")
    if not secret or not provided:
        return False
    return hmac.compare_digest(provided.encode(), secret.encode())


def _parse_ip(value: str) -> str | None:
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        return None


class ContentSecurityPolicyMiddleware:
    """The API returns JSON only, so responses may not load or frame anything."""

    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        policy: str | None = settings.API_CONTENT_SECURITY_POLICY
        if policy and "Content-Security-Policy" not in response:
            response["Content-Security-Policy"] = policy
        return response
