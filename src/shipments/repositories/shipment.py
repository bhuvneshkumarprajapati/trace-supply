from django.db import transaction

from shipments.dtos.shipment import ShipmentDTO
from shipments.models import Shipment, ShipmentEvent


class ShipmentRepository:
    @transaction.atomic
    def create(self, *, origin: str, destination: str) -> ShipmentDTO:
        shipment = Shipment.objects.create(origin=origin, destination=destination)
        ShipmentEvent.objects.create(
            shipment=shipment,
            status=shipment.status,
            location=origin,
            note="Shipment registered",
        )
        return self.get_by_id(shipment.id)

    def get_by_id(self, shipment_id: str) -> ShipmentDTO:
        try:
            shipment = Shipment.objects.prefetch_related("events").get(pk=shipment_id)
        except Shipment.DoesNotExist as exc:
            raise LookupError(f"Shipment {shipment_id} was not found") from exc
        return ShipmentDTO.model_validate(shipment)

    def list_all(self, *, status: str | None = None) -> list[ShipmentDTO]:
        shipments = Shipment.objects.prefetch_related("events")
        if status is not None:
            shipments = shipments.filter(status=status)
        shipments = shipments.order_by("-created_at")
        return [ShipmentDTO.model_validate(shipment) for shipment in shipments]

    @transaction.atomic
    def update_status(
        self,
        *,
        shipment_id: str,
        status: str,
        location: str,
        note: str,
    ) -> ShipmentDTO:
        try:
            shipment = Shipment.objects.select_for_update().get(pk=shipment_id)
        except Shipment.DoesNotExist as exc:
            raise LookupError(f"Shipment {shipment_id} was not found") from exc

        shipment.status = status
        shipment.save(update_fields=["status", "updated_at"])
        ShipmentEvent.objects.create(
            shipment=shipment,
            status=status,
            location=location,
            note=note,
        )
        return self.get_by_id(shipment.id)
