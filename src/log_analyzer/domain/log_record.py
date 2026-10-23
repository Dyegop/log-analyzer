from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address

from pydantic import BaseModel, ConfigDict, Field


class LogRecord(BaseModel):
    """Represent a parsed event with validated fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

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
    destination_ip: IPv4Address | IPv6Address | None = Field(
        default=None,
        description="Destination IP address recorded in the event.",
        examples=["66.102.9.147"],
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
