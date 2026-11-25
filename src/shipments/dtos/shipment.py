from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class ShipmentEventDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    location: str
    note: str
    occurred_at: datetime


class ShipmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    status: str
    origin: str
    destination: str
    events: list[ShipmentEventDTO]

    @field_validator("events", mode="before")
    @classmethod
    def coerce_related_manager(cls, value: Any) -> Any:
        if hasattr(value, "all"):
            return list(value.all())
        return value
