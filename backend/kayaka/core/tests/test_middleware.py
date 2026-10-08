import re

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, override_settings

from kayaka.core.context import get_request_id
from kayaka.core.middleware import RequestContextMiddleware, TrustedProxyMiddleware

SECRET = "test-proxy-secret-0123456789abcdef"


@pytest.fixture
def rf():
    return RequestFactory()


class TestRequestId:
    def run(self, rf, **headers):
        seen = {}

        def view(request):
            seen["request_id"] = get_request_id()
            return HttpResponse("ok")

        response = RequestContextMiddleware(view)(rf.get("/", headers=headers))
        return response, seen["request_id"]

    def test_generates_id_when_missing(self, rf):
        response, inner = self.run(rf)
        assert re.fullmatch(r"req_[0-9a-f]{32}", response["X-Request-ID"])
        assert inner == response["X-Request-ID"]

    def test_accepts_well_formed_incoming_id(self, rf):
        response, _ = self.run(rf, **{"X-Request-ID": "edge-abc12345"})
        assert response["X-Request-ID"] == "edge-abc12345"

    @pytest.mark.parametrize(
        "bad", ["short", "has spaces in it", "x" * 200, "<script>alert</script>"]
    )
    def test_replaces_malformed_incoming_id(self, rf, bad):
        response, _ = self.run(rf, **{"X-Request-ID": bad})
        assert response["X-Request-ID"].startswith("req_")

    def test_context_is_cleared_after_request(self, rf):
        self.run(rf)
        assert get_request_id() is None


class TestTrustedProxy:
    def remote_addr(self, rf, **headers):
        captured = {}

        def view(request):
            captured["ip"] = request.META["REMOTE_ADDR"]
            return HttpResponse("ok")

        request = rf.get("/", REMOTE_ADDR="10.0.0.1", headers=headers)
        TrustedProxyMiddleware(view)(request)
        return captured["ip"]

    def test_trusts_client_ip_with_valid_secret(self, rf):
        ip = self.remote_addr(rf, **{"X-Kayaka-Proxy": SECRET, "X-Kayaka-Client-IP": "203.0.113.7"})
        assert ip == "203.0.113.7"

    def test_ignores_client_ip_without_secret(self, rf):
        assert self.remote_addr(rf, **{"X-Kayaka-Client-IP": "203.0.113.7"}) == "10.0.0.1"

    def test_ignores_client_ip_with_wrong_secret(self, rf):
        headers = {"X-Kayaka-Proxy": "wrong", "X-Kayaka-Client-IP": "203.0.113.7"}
        assert self.remote_addr(rf, **headers) == "10.0.0.1"

    def test_ignores_invalid_ip(self, rf):
        headers = {"X-Kayaka-Proxy": SECRET, "X-Kayaka-Client-IP": "not-an-ip"}
        assert self.remote_addr(rf, **headers) == "10.0.0.1"

    def test_never_trusts_x_forwarded_for(self, rf):
        assert self.remote_addr(rf, **{"X-Forwarded-For": "203.0.113.7"}) == "10.0.0.1"

    @override_settings(PROXY_SHARED_SECRET="")
    def test_empty_secret_disables_trust(self, rf):
        headers = {"X-Kayaka-Proxy": "", "X-Kayaka-Client-IP": "203.0.113.7"}
        assert self.remote_addr(rf, **headers) == "10.0.0.1"

    def test_accepts_ipv6(self, rf):
        headers = {"X-Kayaka-Proxy": SECRET, "X-Kayaka-Client-IP": "2001:db8::1"}
        assert self.remote_addr(rf, **headers) == "2001:db8::1"
