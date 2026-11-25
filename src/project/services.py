import svcs

from shipments.repositories.shipment import ShipmentRepository
from shipments.services.shipment import ShipmentService

registry = svcs.Registry()


def _shipment_service_factory(container: svcs.Container) -> ShipmentService:
    return ShipmentService(container.get(ShipmentRepository))


def register_services(registry: svcs.Registry) -> None:
    """Register application repositories and services."""
    registry.register_factory(ShipmentRepository, ShipmentRepository)
    registry.register_factory(ShipmentService, _shipment_service_factory)


register_services(registry)


def get[T](service_type: type[T]) -> T:
    """Resolve a service from the application registry."""
    return svcs.Container(registry).get(service_type)
