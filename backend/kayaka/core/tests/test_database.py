import pytest
from django.db import connection


@pytest.mark.django_db
def test_database_is_reachable_postgres_17_or_newer():
    assert connection.vendor == "postgresql"
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_setting('server_version_num')::int")
        (version_num,) = cursor.fetchone()
    assert version_num >= 170000


@pytest.mark.django_db
def test_database_round_trip():
    with connection.cursor() as cursor:
        cursor.execute("SELECT %s::text", ["kayaka"])
        assert cursor.fetchone() == ("kayaka",)
