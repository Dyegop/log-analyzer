import csv
from collections.abc import Iterator
from typing import TextIO, override

from log_analyzer.adapters.base_parser import Parser


class CsvParser(Parser):
    """Parse CSV logs."""

    def __init__(self, delimiter: str = ",") -> None:
        self._delimiter = delimiter

    @override
    def _read_fields(self, stream: TextIO) -> Iterator[list[str]]:
        """Read comma-separated fields from a text stream.

        Args:
            stream: Text stream containing CSV log records.
        """
        yield from csv.reader(stream)
