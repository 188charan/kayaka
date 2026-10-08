from drf_spectacular.generators import SchemaGenerator


def test_schema_generates_and_exposes_shared_components():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    assert schema["openapi"].startswith("3.")
    assert "/api/v1/public/ping" in schema["paths"]
    # Infrastructure probes are not part of the API contract.
    assert "/healthz" not in schema["paths"]
    components = schema["components"]["schemas"]
    assert {"PingResponse", "ErrorResponse"} <= set(components)
