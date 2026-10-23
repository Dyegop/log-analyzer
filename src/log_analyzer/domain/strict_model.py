from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Describes a model that rejects unknown fields and prevent attribute reassignment."""

    model_config = ConfigDict(extra="forbid", frozen=True)
