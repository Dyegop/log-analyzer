from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from typing import Any

from pydantic import Field, ValidatorFunctionWrapHandler, field_validator

from log_analyzer.domain.strict_model import StrictModel


class LogRecord(StrictModel):
    """Represent a parsed event with validated fields."""

    timestamp: Decimal | None = Field(
        default=None,
        allow_inf_nan=False,
        description="Event timestamp in Unix seconds.",
        examples=["1157689324.156"],
    )
    client_ip: IPv4Address | IPv6Address | None = Field(
        default=None,
        description="Client IP address recorded in the event.",
        examples=["10.105.21.199"],
    )
    response_header_bytes: int | None = Field(
        default=None,
        ge=0,
        description="Response header size in bytes.",
        examples=[1372],
    )
    response_bytes: int | None = Field(
        default=None,
        ge=0,
        description="Response size in bytes recorded in the event.",
        examples=[399],
    )

    @field_validator("*", mode="wrap")
    @classmethod
    def normalize_field(cls, value: Any, handler: ValidatorFunctionWrapHandler) -> Any:
        """Validate each field and normalize invalid values to None."""
        try:
            return handler(value)
        except ValueError:
            return None
