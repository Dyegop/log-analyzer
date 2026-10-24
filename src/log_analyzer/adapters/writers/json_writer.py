from log_analyzer.adapters.writers.base_writer import Writer
from log_analyzer.domain import AggregateResults


class JsonWriter(Writer):
    """Write aggregate results to a JSON file."""

    def write(self, results: AggregateResults) -> None:
        payload = results.model_dump_json(exclude_unset=True, indent=2)
        temporary = self._output.with_name(self._output.name + ".tmp")

        stream = temporary.open("x", encoding="utf-8")
        try:
            with stream:
                stream.write(payload)
            temporary.replace(self._output)
        finally:
            temporary.unlink(missing_ok=True)
