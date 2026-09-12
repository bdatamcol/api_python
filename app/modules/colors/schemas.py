import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ColorBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=120,
        examples=["Negro Mate"],
    )

    hex_code: str | None = Field(
        default=None,
        max_length=7,
        examples=["#1C1C1C"],
    )

    @field_validator("hex_code")
    @classmethod
    def validate_hex_code(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip().upper()

        if not re.fullmatch(r"#[0-9A-F]{6}", value):
            raise ValueError(
                "hex_code debe tener formato hexadecimal válido, por ejemplo #1C1C1C"
            )

        return value


class ColorCreate(ColorBase):
    pass


class ColorUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=120,
    )

    hex_code: str | None = Field(
        default=None,
        max_length=7,
    )

    active: bool | None = None

    @field_validator("hex_code")
    @classmethod
    def validate_hex_code(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip().upper()

        if not re.fullmatch(r"#[0-9A-F]{6}", value):
            raise ValueError(
                "hex_code debe tener formato hexadecimal válido, por ejemplo #1C1C1C"
            )

        return value


class ColorResponse(ColorBase):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID
    slug: str
    active: bool
    created_at: datetime
    updated_at: datetime
