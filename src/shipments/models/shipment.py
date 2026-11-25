from typing import ClassVar

from django.db import models

from project.ids import generate_evt_id, generate_shp_id
from shipments.statuses import SHIPMENT_STATUS_CHOICES


class Shipment(models.Model):
    class Meta:
        verbose_name = "shipment"
        verbose_name_plural = "shipments"
        indexes = (
            models.Index(fields=["status", "-created_at"], name="idx_shipment_status_recent"),
            models.Index(fields=["-created_at"], name="idx_shipment_created"),
        )

    __prefix__: ClassVar[str] = "shp"

    id = models.CharField(max_length=64, primary_key=True, default=generate_shp_id, editable=False)

    created_at = models.DateTimeField(verbose_name="created at", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="updated at", auto_now=True)

    status = models.CharField(
        max_length=20,
        choices=SHIPMENT_STATUS_CHOICES,
        default="pending",
    )

    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"Shipment {self.id}: {self.status}"


class ShipmentEvent(models.Model):
    class Meta:
        verbose_name = "shipment event"
        verbose_name_plural = "shipment events"
        indexes = (
            models.Index(
                fields=["shipment", "-occurred_at"],
                name="idx_shipment_event_timeline",
            ),
        )
        ordering = ("-occurred_at",)

    __prefix__: ClassVar[str] = "evt"

    id = models.CharField(max_length=64, primary_key=True, default=generate_evt_id, editable=False)

    occurred_at = models.DateTimeField(verbose_name="occurred at", auto_now_add=True)

    status = models.CharField(max_length=20, choices=SHIPMENT_STATUS_CHOICES)

    location = models.CharField(max_length=255)
    note = models.TextField(blank=True)

    shipment = models.ForeignKey(
        Shipment,
        verbose_name="shipment",
        related_name="events",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.shipment_id} {self.status} at {self.location}"
