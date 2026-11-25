import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_authenticated_create_update_and_public_tracking_lookup(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="operator", password="test-pass")
    client.force_login(user)

    created = client.post(
        "/api/shipments/",
        data={"origin": "Port A", "destination": "Warehouse B"},
        content_type="application/json",
    )

    assert created.status_code == 201
    shipment_id = created.json()["id"]
    assert shipment_id.startswith("shp_")
    assert created.json()["events"][0]["status"] == "pending"

    updated = client.patch(
        f"/api/shipments/{shipment_id}/status/",
        data={
            "status": "in_transit",
            "location": "Port A terminal",
            "note": "Loaded",
        },
        content_type="application/json",
    )

    assert updated.status_code == 200
    assert updated.json()["status"] == "in_transit"
    assert len(updated.json()["events"]) == 2

    tracked = client.get(f"/api/shipments/{shipment_id}/")

    assert tracked.status_code == 200
    assert tracked.json()["destination"] == "Warehouse B"


@pytest.mark.django_db
def test_shipment_writes_require_authentication(client):
    response = client.post(
        "/api/shipments/",
        data={"origin": "Port A", "destination": "Warehouse B"},
        content_type="application/json",
    )

    assert response.status_code == 401
