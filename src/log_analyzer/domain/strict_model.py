from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Describes a BaseModel with forbidden extra fields and field reassignment."""

    model_config = ConfigDict(extra="forbid", frozen=True)
