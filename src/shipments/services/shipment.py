from typing import ClassVar

from shipments.dtos.shipment import ShipmentDTO
from shipments.repositories.shipment import ShipmentRepository
from shipments.statuses import ShipmentStatus


class ShipmentService:
    _allowed_transitions: ClassVar[dict[ShipmentStatus, frozenset[ShipmentStatus]]] = {
        ShipmentStatus.PENDING: frozenset({ShipmentStatus.IN_TRANSIT, ShipmentStatus.CANCELLED}),
        ShipmentStatus.IN_TRANSIT: frozenset({ShipmentStatus.DELIVERED, ShipmentStatus.CANCELLED}),
        ShipmentStatus.DELIVERED: frozenset(),
        ShipmentStatus.CANCELLED: frozenset(),
    }

    def __init__(self, repo: ShipmentRepository):
        self.repo = repo

    def create_shipment(self, *, origin: str, destination: str) -> ShipmentDTO:
        origin = origin.strip()
        destination = destination.strip()
        if not origin or not destination:
            raise ValueError("Origin and destination are required")
        if origin.casefold() == destination.casefold():
            raise ValueError("Origin and destination must be different")
        return self.repo.create(origin=origin, destination=destination)

    def list_shipments(self, *, status: str | None = None) -> list[ShipmentDTO]:
        if status is not None:
            try:
                status = ShipmentStatus(status).value
            except ValueError:
                raise ValueError(f"Unknown shipment status: {status}") from None
        return self.repo.list_all(status=status)

    def get_shipment(self, shipment_id: str) -> ShipmentDTO:
        return self.repo.get_by_id(shipment_id)

    def update_status(
        self,
        *,
        shipment_id: str,
        status: str,
        location: str,
        note: str = "",
    ) -> ShipmentDTO:
        try:
            next_status = ShipmentStatus(status)
        except ValueError:
            raise ValueError(f"Unknown shipment status: {status}") from None

        current = self.repo.get_by_id(shipment_id)
        if next_status not in self._allowed_transitions[ShipmentStatus(current.status)]:
            raise ValueError(f"Cannot change shipment from {current.status} to {next_status.value}")

        location = location.strip()
        if not location:
            raise ValueError("Location is required")

        return self.repo.update_status(
            shipment_id=shipment_id,
            status=next_status.value,
            location=location,
            note=note.strip(),
        )
