"""Command-line entry point."""

import argparse
from pathlib import Path


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
    operations = parser.add_argument_group("operations", "Select one or more operations.")
    operations.add_argument("--mfip", action="store_true", help="Calculate the most frequent client IP.")
    operations.add_argument("--lfip", action="store_true", help="Calculate the least frequent client IP.")
    operations.add_argument("--eps", action="store_true", help="Calculate events per second.")
    operations.add_argument("--bytes", action="store_true", help="Calculate the total bytes exchanged.")

    arguments = parser.parse_args(argv)

    if not any((arguments.mfip, arguments.lfip, arguments.eps, arguments.bytes)):
        parser.error("select at least one operation: --mfip, --lfip, --eps, or --bytes")

    return arguments


def main() -> int:
    """Parse command-line arguments."""
    parse_arguments()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
