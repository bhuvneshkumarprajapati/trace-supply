import pytest
from django.contrib.auth import get_user_model


def test_home_redirects_anonymous_user_to_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response["Location"].startswith("/accounts/login/?next=/")


@pytest.mark.django_db
def test_authenticated_user_gets_dashboard(client):
    user = get_user_model().objects.create_user(username="operator", password="secret")
    client.force_login(user)

    response = client.get("/")

    assert response.status_code == 200
    assert b"Shipment control" in response.content


def test_openapi_schema_is_mounted(client):
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    assert response.json()["openapi"]
