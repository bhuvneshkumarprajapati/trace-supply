from django.http import HttpRequest
from ninja import Router, Status
from ninja.security import django_auth

from project.services import get
from project.types import AuthedRequest
from shipments.dtos.shipment import ShipmentDTO
from shipments.services.shipment import ShipmentService

from .schemas import CreateShipmentIn, UpdateShipmentStatusIn

router = Router()


@router.get("/", response=list[ShipmentDTO], auth=django_auth)
def list_shipments(request: AuthedRequest, status: str | None = None):
    return get(ShipmentService).list_shipments(status=status)


@router.post("/", response={201: ShipmentDTO}, auth=django_auth)
def create_shipment(request: AuthedRequest, payload: CreateShipmentIn):
    shipment = get(ShipmentService).create_shipment(
        origin=payload.origin,
        destination=payload.destination,
    )
    return Status(201, shipment)


@router.get("/{shipment_id}/", response=ShipmentDTO)
def get_shipment(request: HttpRequest, shipment_id: str):
    return get(ShipmentService).get_shipment(shipment_id)


@router.patch("/{shipment_id}/status/", response=ShipmentDTO, auth=django_auth)
def update_shipment_status(
    request: AuthedRequest,
    shipment_id: str,
    payload: UpdateShipmentStatusIn,
):
    return get(ShipmentService).update_status(
        shipment_id=shipment_id,
        status=payload.status,
        location=payload.location,
        note=payload.note,
    )
