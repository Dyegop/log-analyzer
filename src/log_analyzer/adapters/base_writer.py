from abc import ABC, abstractmethod
from pathlib import Path

from log_analyzer.domain import AggregateResults


class Writer(ABC):
    """Write aggregate results to the given output Path."""

    def __init__(self, output: Path) -> None:
        self._output = output

    @abstractmethod
    def write(self, results: AggregateResults) -> None:
        """Write aggregation results atomically."""
        ...
