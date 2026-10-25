import json
from pathlib import Path
from typing import Any

import pytest

from log_analyzer.cli import main
from tests.helpers import LogRow


class TestCli:
    @pytest.mark.parametrize(
        ("arguments", "expected"),
        [
            pytest.param(["--mfip"], {"mfip": [{"ip": "192.0.2.1", "count": 2}]}),
            pytest.param(["--lfip"], {"lfip": [{"ip": "192.0.2.2", "count": 1}]}),
            pytest.param(["--eps", "--bytes"], {"eps": 1.5, "bytes": 330}),
        ],
    )
    def test_run_only_selected_operations(self, tmp_path: Path, arguments: list[str], expected: dict[str, Any]) -> None:
        # Given three LogRow and an output file
        source = tmp_path / "access.log"
        source.write_text(
            LogRow(timestamp="1000").to_line()
            + LogRow(timestamp="1001").to_line()
            + LogRow(timestamp="1002", client_ip="192.0.2.2").to_line(),
            encoding="utf-8",
        )
        output = tmp_path / "results"

        # When requesting the selected arguments
        exit_code = main([str(source), str(output), *arguments])

        # Then the JSON output contains exactly the requested results
        assert exit_code == 0
        assert json.loads((tmp_path / "results.json").read_text(encoding="utf-8")) == expected

    def test_combines_all_input_files(self, tmp_path: Path) -> None:
        # Given two input files with different bytes exchange
        log_1 = tmp_path / "log_1.log"
        log_2 = tmp_path / "log_2.log"
        log_1.write_text(LogRow().to_line(), encoding="utf-8")
        log_2.write_text(LogRow(header_bytes="20", response_bytes="200").to_line(), encoding="utf-8")

        output = tmp_path / "results"

        # When passing both input paths to the CLI
        exit_code = main([str(log_1), str(log_2), str(output), "--bytes"])

        # Then output file should include both file results
        assert exit_code == 0
        assert json.loads((tmp_path / "results.json").read_text(encoding="utf-8")) == {"bytes": 330}

    @pytest.mark.parametrize(
        "arguments",
        [
            ["access.log", "results"],
            ["access.log", "results", "--bytes", "--delimiter", "ab"],
            ["access.log", "results.json", "--bytes"],
        ],
    )
    def test_rejects_invalid_arguments(self, arguments: list[str]) -> None:
        # When passing invalid arguments
        with pytest.raises(SystemExit) as error:
            main(arguments)

        # Then the CLI reports an argument error
        assert error.value.code == 2

    def test_saves_results_when_a_record_is_invalid(self, tmp_path: Path) -> None:
        # Given a valid log row followed by an invalid one
        source = tmp_path / "access.log"
        source.write_text(LogRow().to_line() + "malformed", encoding="utf-8")
        output = tmp_path / "results"

        # When analyzing the file
        exit_code = main([str(source), str(output), "--bytes"])

        # Then valid results are saved and the exit code indicates partial success
        assert exit_code == 3
        assert json.loads(output.with_suffix(".json").read_text(encoding="utf-8")) == {"bytes": 110}

    def test_saves_results_when_a_file_is_missing(self, tmp_path: Path) -> None:
        # Given a missing file followed by a valid one
        source = tmp_path / "access.log"
        source.write_text(LogRow().to_line(), encoding="utf-8")
        missing = tmp_path / "missing.log"
        output = tmp_path / "results"

        # When analyzing both files
        exit_code = main([str(missing), str(source), str(output), "--bytes"])

        # Then valid results are saved and the exit code indicates partial success
        assert exit_code == 3
        assert json.loads(output.with_suffix(".json").read_text(encoding="utf-8")) == {"bytes": 110}

    def test_preserves_existing_output(self, tmp_path: Path) -> None:
        # Given empty input and previously saved results
        source = tmp_path / "access.log"
        source.write_text("", encoding="utf-8")
        saved = tmp_path / "results.json"
        saved.write_text('{"bytes": 42}', encoding="utf-8")

        # When analysis has no usable events
        exit_code = main([str(source), str(tmp_path / "results"), "--bytes"])

        # Then failure leaves the previous results intact
        assert exit_code == 1
        assert saved.read_text(encoding="utf-8") == '{"bytes": 42}'

    def test_accepts_custom_csv_delimiter(self, tmp_path: Path) -> None:
        # Given a semicolon-separated log record
        source = tmp_path / "access.csv"
        source.write_text(LogRow().to_line(delimiter=";"), encoding="utf-8")
        output = tmp_path / "results"

        # When selecting the matching CSV delimiter
        exit_code = main([str(source), str(output), "--bytes", "--delimiter", ";"])

        # Then the record is parsed correctly
        assert exit_code == 0
        assert json.loads((tmp_path / "results.json").read_text(encoding="utf-8")) == {"bytes": 110}

    def test_rejects_matching_input_and_output_names(self, tmp_path: Path) -> None:
        # Given input and output with the same base name
        source = tmp_path / "results.log"
        source.write_text(LogRow().to_line(), encoding="utf-8")
        output = tmp_path / "results"

        # When analyzing the file
        exit_code = main([str(source), str(output), "--bytes"])

        # Then the CLI rejects the name conflict
        assert exit_code == 1
        assert not output.with_suffix(".json").exists()

    def test_reports_output_failure(self, tmp_path: Path) -> None:
        # Given valid input and a missing output directory
        source = tmp_path / "access.log"
        source.write_text(LogRow().to_line(), encoding="utf-8")
        output = tmp_path / "missing" / "results"

        # When saving the results
        exit_code = main([str(source), str(output), "--bytes"])

        # Then the CLI reports failure
        assert exit_code == 1
