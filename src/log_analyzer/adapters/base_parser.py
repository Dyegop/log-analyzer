"""Base generic parser with shared logic."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TextIO

from src.log_analyzer.domain import LogRecord

logger: logging.Logger = logging.getLogger(__name__)


class Parser(ABC):
    """
    Convert rows from given files into normalized log records.

    Fields are identified based on their position, rather than inferred from their values.
    Concrete parsers handle the file format while sharing the same field order and meanings.
    """

    def parse(self, stream: TextIO) -> Iterator[LogRecord]:
        """Parse records, ignoring invalid rows.

        Args:
            stream: Text stream containing log records.

        Yields:
            Validated log records in source order.
        """

        rejected_count = 0

        for row_number, fields in enumerate(self._read_fields(stream), start=1):
            try:
                record = self._build_record(fields)
            except ValueError:
                rejected_count += 1
                logger.warning("Skipping invalid record at row %s", row_number)
                continue
            yield record

        if rejected_count:
            logger.warning("Rejected %s invalid records", rejected_count)

    @abstractmethod
    def _read_fields(self, stream: TextIO) -> Iterator[list[str]]:
        """Read rows using the concrete format's syntax.

        Args:
            stream: Text stream containing log records.

        Yields:
            Field values for each record.
        """
        ...

    @staticmethod
    def _build_record(fields: list[str]) -> LogRecord:
        """
        Map file fields into a domain record.

        Raises:
            ValueError: If the row structure or field values are invalid.
        """

        if len(fields) != 10:
            raise ValueError(f"Expected ten fields, found {len(fields)}.")

        # Parsing for field holding `Type of access/destination IP address`
        access_type, separator, destination = fields[8].partition("/")
        if not separator or not access_type or not destination:
            raise ValueError("Expected the destination field in access-type/destination IP address format.")

        return LogRecord.model_validate(
            {
                "timestamp": fields[0],
                "client_ip": fields[2],
                "destination_ip": destination,
                "response_header_bytes": fields[1],
                "response_bytes": fields[4],
            }
        )
