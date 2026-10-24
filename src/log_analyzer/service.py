"""Coordinate input reading and log parsing."""

import csv
import gzip
import logging
from collections.abc import Generator, Iterator
from contextlib import closing
from pathlib import Path
from typing import TextIO
from zlib import error as ZlibError

from log_analyzer.adapters import CsvParser, Parser, TxtParser
from log_analyzer.domain import (
    CSV_EXTENSION,
    GZIP_EXTENSION,
    LOG_EXTENSION,
    SUPPORTED_EXTENSIONS,
    TXT_EXTENSION,
    AggregateResults,
    LogAggregates,
    LogRecord,
)

logger: logging.Logger = logging.getLogger(__name__)


class LogAnalyzerService:
    """Reads log files and run analytics."""

    def __init__(self, delimiter: str = ",") -> None:
        """Configure the supported input parsers.

        Args:
            delimiter: Field separator used for CSV files. Defaults to comma.
        """

        txt_parser = TxtParser()
        self._parsers: dict[str, Parser] = {
            LOG_EXTENSION: txt_parser,
            TXT_EXTENSION: txt_parser,
            CSV_EXTENSION: CsvParser(delimiter=delimiter),
        }

    def analyze(
        self,
        paths: list[Path],
        *,
        mfip: bool = False,
        lfip: bool = False,
        eps: bool = False,
        bytes_exchanged: bool = False,
    ) -> AggregateResults:
        """Calculate selected aggregates across the input files.

        Args:
            paths: Input paths to read and parse.
            mfip: Calculate the most frequent IPs across both fields.
            lfip: Calculate the least frequent IPs across both fields.
            eps: Calculate average events per second for timestamped records.
            bytes_exchanged: Sum response header and response bytes.

        Returns:
            Typed results for the selected operations.
        """

        aggregates = LogAggregates(mfip=mfip, lfip=lfip, eps=eps, bytes_exchanged=bytes_exchanged)

        with closing(self._read_records(paths)) as records:
            for record in records:
                aggregates.aggregate(record)

        return aggregates.produce_results()

    def _read_records(self, paths: list[Path]) -> Generator[LogRecord, None, None]:
        """Read and parse supported files, ignoring failures.

        Args:
            paths: Paths to plain or gzip-compressed log files.

        Yields:
            Validated records from supported input file extensions.
        """

        for file_ext, stream in self._read_files(paths):
            parser = self._parsers.get(Path(file_ext).suffix.lower())
            if parser is None:
                logger.warning("Skipping unsupported input file_ext: %s", file_ext)
                continue

            logger.info("Processing input file_ext: %s", file_ext)
            try:
                yield from parser.parse(stream)
            except (OSError, EOFError, UnicodeDecodeError, csv.Error, ZlibError):
                logger.warning("Unable to finish reading input file_ext: %s", file_ext)

    @staticmethod
    def _read_files(paths: list[Path]) -> Iterator[tuple[str, TextIO]]:
        """Open plain or gzip-compressed input files as text streams.

        Args:
            paths: Input paths to process in order.

        Yields:
            File extension and open UTF-8 text streams.
        """

        for path in paths:
            extension = path.suffix.lower()
            if extension not in SUPPORTED_EXTENSIONS:
                logger.warning("Skipping unsupported input file: %s", path)
                continue

            try:
                if extension == GZIP_EXTENSION:
                    with gzip.open(path, "rt", encoding="utf-8", newline="") as stream:
                        yield str(path.with_suffix("")), stream
                else:
                    with path.open("r", encoding="utf-8", newline="") as stream:
                        yield str(path), stream
            except OSError:
                logger.warning("Unable to open input file: %s", path)
