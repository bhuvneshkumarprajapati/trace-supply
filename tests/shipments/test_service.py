from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from shipments.dtos.shipment import ShipmentDTO
from shipments.repositories.shipment import ShipmentRepository
from shipments.services.shipment import ShipmentService


def make_shipment(status: str = "pending") -> ShipmentDTO:
    timestamp = datetime(2026, 1, 1, tzinfo=UTC)
    return ShipmentDTO(
        id="shp_test",
        created_at=timestamp,
        updated_at=timestamp,
        status=status,
        origin="Port A",
        destination="Warehouse B",
        events=[],
    )


def test_create_shipment_normalizes_route_and_delegates():
    repo = MagicMock(spec=ShipmentRepository)
    expected = make_shipment()
    repo.create.return_value = expected

    result = ShipmentService(repo).create_shipment(
        origin=" Port A ",
        destination=" Warehouse B ",
    )

    assert result is expected
    repo.create.assert_called_once_with(origin="Port A", destination="Warehouse B")


def test_create_rejects_identical_origin_and_destination():
    repo = MagicMock(spec=ShipmentRepository)

    with pytest.raises(ValueError, match="must be different"):
        ShipmentService(repo).create_shipment(origin="Port A", destination=" port a ")

    repo.create.assert_not_called()


def test_status_transition_delegates_after_validation():
    repo = MagicMock(spec=ShipmentRepository)
    repo.get_by_id.return_value = make_shipment("pending")
    expected = make_shipment("in_transit")
    repo.update_status.return_value = expected

    result = ShipmentService(repo).update_status(
        shipment_id="shp_test",
        status="in_transit",
        location=" Port A terminal ",
        note=" Loaded ",
    )

    assert result is expected
    repo.update_status.assert_called_once_with(
        shipment_id="shp_test",
        status="in_transit",
        location="Port A terminal",
        note="Loaded",
    )


def test_terminal_shipment_cannot_transition():
    repo = MagicMock(spec=ShipmentRepository)
    repo.get_by_id.return_value = make_shipment("delivered")

    with pytest.raises(ValueError, match="Cannot change shipment"):
        ShipmentService(repo).update_status(
            shipment_id="shp_test",
            status="in_transit",
            location="Warehouse B",
        )

    repo.update_status.assert_not_called()
