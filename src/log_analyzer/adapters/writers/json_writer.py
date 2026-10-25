import tempfile
from pathlib import Path

from log_analyzer.adapters.writers.base_writer import Writer
from log_analyzer.domain import AggregateResults


class JsonWriter(Writer):
    """Write aggregate results to a JSON file."""

    def write(self, results: AggregateResults) -> None:
        output = self._output.with_name(f"{self._output.name}.json")
        payload = results.model_dump_json(exclude_unset=True, indent=2)
        tmp_file: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=output.parent,
                prefix=f".{output.name}.",
                suffix=".tmp",
                delete=False,
            ) as output_file:
                tmp_file = Path(output_file.name)
                output_file.write(payload)

            tmp_file.replace(output)

        finally:
            if tmp_file:
                tmp_file.unlink(missing_ok=True)
