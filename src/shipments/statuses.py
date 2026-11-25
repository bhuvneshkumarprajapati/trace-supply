from enum import StrEnum


class ShipmentStatus(StrEnum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


SHIPMENT_STATUS_CHOICES = [
    (status.value, status.name.replace("_", " ").title()) for status in ShipmentStatus
]
