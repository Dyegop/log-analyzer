from ipaddress import IPv4Address, IPv6Address

from pydantic import Field

from log_analyzer.domain.strict_model import StrictModel


class IPFrequency(StrictModel):
    """An IP address with its occurrence count."""

    ip: IPv4Address | IPv6Address = Field(
        description="Client IP address.",
        examples=["10.0.0.1"],
    )
    count: int = Field(
        ge=1,
        description="Number of occurrences.",
        examples=[3],
    )


class AggregateResults(StrictModel):
    """Selected aggregate operation results."""

    mfip: list[IPFrequency] | None = Field(
        default=None,
        description="All IPs tied for the highest frequency.",
        examples=[[{"ip": "10.0.0.1", "count": 3}]],
    )
    lfip: list[IPFrequency] | None = Field(
        default=None,
        description="All IPs tied for the lowest frequency.",
        examples=[[{"ip": "192.0.2.1", "count": 1}]],
    )
    eps: float | None = Field(
        default=None,
        ge=0,
        allow_inf_nan=False,
        description="Average timestamped events per second.",
        examples=[5.0],
    )
    bytes: int | None = Field(
        default=None,
        ge=0,
        description="Sum of response header and response byte values.",
        examples=[1771],
    )
