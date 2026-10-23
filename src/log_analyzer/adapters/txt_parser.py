from collections.abc import Iterator
from typing import TextIO, override

from log_analyzer.adapters.base_parser import Parser


class TxtParser(Parser):
    """Parse whitespace-separated text logs."""

    @override
    def _read_fields(self, stream: TextIO) -> Iterator[list[str]]:
        """Read whitespace-separated fields from a text stream.

        Args:
            stream: Text stream containing log records.
        """
        for line in stream:
            yield line.split()
