from pydantic import BaseModel, Field


class Metrics(BaseModel):
    """Metrics for accepted records, rejected records, and failed files."""

    accepted_records: int = Field(
        default=0,
        ge=0,
        description="Number of records successfully aggregated.",
        examples=[100],
    )
    rejected_records: int = Field(
        default=0,
        ge=0,
        description="Number of rows rejected during parsing.",
        examples=[2],
    )
    failed_files: int = Field(
        default=0,
        ge=0,
        description="Number of unsupported or unreadable input sources.",
        examples=[1],
    )

    @property
    def has_failures(self) -> bool:
        return bool(self.rejected_records or self.failed_files)
