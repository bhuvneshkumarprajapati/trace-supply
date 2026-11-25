import pytest

from shipments.dtos.shipment import ShipmentDTO
from shipments.repositories.shipment import ShipmentRepository


@pytest.mark.django_db
def test_create_and_update_returns_shipment_dto_with_prefixed_ids():
    repo = ShipmentRepository()

    shipment = repo.create(origin="Port A", destination="Warehouse B")

    assert isinstance(shipment, ShipmentDTO)
    assert shipment.id.startswith("shp_")
    assert shipment.status == "pending"
    assert len(shipment.events) == 1
    assert shipment.events[0].id.startswith("evt_")
    assert shipment.events[0].location == "Port A"

    updated = repo.update_status(
        shipment_id=shipment.id,
        status="in_transit",
        location="Port A terminal",
        note="Loaded onto vessel",
    )

    assert updated.status == "in_transit"
    assert len(updated.events) == 2
    assert updated.events[0].status == "in_transit"
    assert updated.events[0].note == "Loaded onto vessel"


@pytest.mark.django_db
def test_list_all_filters_by_status():
    repo = ShipmentRepository()
    pending = repo.create(origin="Port A", destination="Depot A")
    other_pending = repo.create(origin="Port B", destination="Depot B")
    repo.update_status(
        shipment_id=pending.id,
        status="in_transit",
        location="Port A terminal",
        note="Loaded",
    )

    results = repo.list_all(status="pending")

    assert [shipment.id for shipment in results] == [other_pending.id]
    assert [shipment.id for shipment in repo.list_all(status="in_transit")] == [pending.id]
