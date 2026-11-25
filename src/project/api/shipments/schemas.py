from ninja import Schema


class CreateShipmentIn(Schema):
    origin: str
    destination: str


class UpdateShipmentStatusIn(Schema):
    status: str
    location: str
    note: str = ""
