"""Command-line entry point."""

import argparse
import csv
import logging
from pathlib import Path

from log_analyzer.adapters.json_writer import JsonWriter
from log_analyzer.service import LogAnalyzerService

logger = logging.getLogger(__name__)


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parse input user arguments. Available operations are:
        - Arguments:
            input: Path to one or more input files.
            output: Path to a file to save output in plain text JSON format.
        - Options:
            mfip: the most frequent IP
            lfip: the least frequent IP
            eps: numbered of events per second
            bytes: the total amount of bytes exchanged

    Args:
        argv: Arguments to parse; defaults to the process command-line arguments.

    Returns:
        Parsed file paths and operation flags.

    Raises:
        SystemExit: If help is requested or the arguments are invalid.
    """
    parser = argparse.ArgumentParser(
        description="Analyze the content of log files.",
        epilog="Example: log-analyzer access.log another.log results.json --mfip --bytes",
    )
    parser.add_argument("input", nargs="+", type=Path, help="Paths to one or more input log files.")
    parser.add_argument("output", type=Path, help="Path to the output JSON file.")
    parser.add_argument("--delimiter", default=",", help="CSV field separator (default: comma).")
    operations = parser.add_argument_group("operations", "Select one or more operations.")
    operations.add_argument("--mfip", action="store_true", help="Calculate the most frequent IPs.")
    operations.add_argument("--lfip", action="store_true", help="Calculate the least frequent IPs.")
    operations.add_argument("--eps", action="store_true", help="Calculate events per second.")
    operations.add_argument("--bytes", action="store_true", help="Calculate the total bytes exchanged.")

    arguments = parser.parse_args(argv)

    if not any((arguments.mfip, arguments.lfip, arguments.eps, arguments.bytes)):
        parser.error("select at least one operation: --mfip, --lfip, --eps, or --bytes")

    try:
        csv.reader([], delimiter=arguments.delimiter)
    except (TypeError, ValueError):
        parser.error("--delimiter must be a single character accepted by the CSV reader")

    return arguments


def main(argv: list[str] | None = None) -> int:
    """Analyze inputs and write JSON; return 0 for success, 1 for failure, 3 for partial results."""

    arguments = parse_arguments(argv)
    service = LogAnalyzerService(delimiter=arguments.delimiter)

    try:
        if any(arguments.output.resolve() == path.resolve() for path in arguments.input):
            raise ValueError("Output must not overwrite an input file.")

        results = service.analyze(
            arguments.input,
            mfip=arguments.mfip,
            lfip=arguments.lfip,
            eps=arguments.eps,
            bytes_exchanged=arguments.bytes,
        )
        writer = JsonWriter(arguments.output)
        writer.write(results)

    except (OSError, ValueError):
        logger.error("Analysis or output failed, no results were saved.")
        return 1

    logger.info("Results saved to %s", arguments.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
