import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class InventoryBase(BaseModel):
    variant_id: uuid.UUID

    store_id: uuid.UUID

    quantity: int = Field(
        default=0,
        ge=0,
        examples=[5],
    )

    reserved_quantity: int = Field(
        default=0,
        ge=0,
        examples=[1],
    )

    @model_validator(mode="after")
    def validate_reserved_quantity(self):
        if self.reserved_quantity > self.quantity:
            raise ValueError(
                "La cantidad reservada no puede ser mayor que la cantidad física"
            )

        return self


class InventoryCreate(InventoryBase):
    pass


class InventoryCreateForVariant(BaseModel):
    store_id: uuid.UUID

    quantity: int = Field(
        default=0,
        ge=0,
        examples=[5],
    )

    reserved_quantity: int = Field(
        default=0,
        ge=0,
        examples=[1],
    )

    @model_validator(mode="after")
    def validate_reserved_quantity(self):
        if self.reserved_quantity > self.quantity:
            raise ValueError(
                "La cantidad reservada no puede ser mayor que la cantidad física"
            )

        return self


class InventoryUpdate(BaseModel):
    quantity: int | None = Field(
        default=None,
        ge=0,
    )

    reserved_quantity: int | None = Field(
        default=None,
        ge=0,
    )

    @model_validator(mode="after")
    def validate_values(self):
        if (
            self.quantity is not None
            and self.reserved_quantity is not None
            and self.reserved_quantity > self.quantity
        ):
            raise ValueError(
                "La cantidad reservada no puede ser mayor que la cantidad física"
            )

        return self


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    available_quantity: int

    updated_at: datetime
