import gzip
from pathlib import Path

import pytest

from log_analyzer.service import LogAnalyzerService
from tests.helpers import LogRow


class TestLogAnalyzerService:
    @pytest.mark.parametrize("suffix", [".txt", ".csv", ".log.gz", ".csv.gz"])
    def test_reads_supported_formats(self, tmp_path: Path, suffix: str) -> None:
        # Given one log file in a supported input format
        source = tmp_path / f"access{suffix}"
        row = LogRow().to_line(delimiter="," if ".csv" in suffix else " ")
        source.write_bytes(gzip.compress(row.encode()) if suffix.endswith(".gz") else row.encode())
        service = LogAnalyzerService()

        # When calculating the available bytes
        result = service.analyze([source], bytes_exchanged=True)

        # Then the input is processed successfully
        assert result.bytes == 110
        assert service.metrics.accepted_records == 1
        assert service.metrics.failed_files == 0

    @pytest.mark.parametrize(
        "invalid_row",
        [
            pytest.param("malformed\n"),
            pytest.param("\n"),
            pytest.param(LogRow(timestamp="bad", client_ip="bad", header_bytes="-1", response_bytes="-1").to_line()),
        ],
    )
    def test_skips_invalid_rows_and_continues(self, tmp_path: Path, invalid_row: str) -> None:
        # Given an unusable record followed by a valid event
        source = tmp_path / "access.log"
        source.write_text(invalid_row + LogRow().to_line(), encoding="utf-8")
        service = LogAnalyzerService()

        # When processing the file
        result = service.analyze([source], bytes_exchanged=True)

        # Then the valid event contributes and the rejected record is counted
        assert result.bytes == 110
        assert service.metrics.accepted_records == 1
        assert service.metrics.rejected_records == 1
        assert service.metrics.failed_files == 0

    def test_counts_ip_frequencies(self, tmp_path: Path) -> None:
        # Given one client appearing twice and another appearing once
        source = tmp_path / "access.log"
        source.write_text(
            LogRow(client_ip="192.0.2.1").to_line() * 2 + LogRow(client_ip="192.0.2.2").to_line(),
            encoding="utf-8",
        )

        # When requesting the most and least frequent IPs
        result = LogAnalyzerService().analyze([source], mfip=True, lfip=True)

        # Then each result identifies the expected IP and count
        assert [(str(ip.ip), ip.count) for ip in result.mfip] == [("192.0.2.1", 2)]
        assert [(str(ip.ip), ip.count) for ip in result.lfip] == [("192.0.2.2", 1)]

    def test_averages_timestamped_events_across_unordered_files(self, tmp_path: Path) -> None:
        # Given invalid timestamps
        log_1 = tmp_path / "log_1.log"
        log_2 = tmp_path / "log_2.log"
        log_1.write_text(LogRow(timestamp="1.5").to_line() + LogRow(timestamp="bad").to_line(), encoding="utf-8")
        log_2.write_text(LogRow(timestamp="-0.5").to_line() + LogRow(timestamp="0").to_line(), encoding="utf-8")

        # When calculating the overall average rate
        result = LogAnalyzerService().analyze([log_1, log_2], eps=True)

        # Then only valid timestamped events contribute
        assert result.eps == 1.5

    def test_zero_duration_does_not_stop_processing(self, tmp_path: Path) -> None:
        # Given two records with the same timestamp
        source = tmp_path / "access.log"
        source.write_text(LogRow(timestamp="1000").to_line() * 2, encoding="utf-8")

        # When calculating EPS and bytes
        result = LogAnalyzerService().analyze([source], eps=True, bytes_exchanged=True)

        # Then zero duration makes EPS unavailable without preventing other results
        assert result.eps is None
        assert result.bytes == 220

    def test_sums_available_byte_fields(self, tmp_path: Path) -> None:
        # Given records with both byte fields, only response bytes, and only header bytes
        source = tmp_path / "access.log"
        source.write_text(
            LogRow().to_line()
            + LogRow(header_bytes="-", response_bytes="20").to_line()
            + LogRow(header_bytes="30", response_bytes="-").to_line(),
            encoding="utf-8",
        )

        # When calculating the byte total
        result = LogAnalyzerService().analyze([source], bytes_exchanged=True)

        # Then every available byte value contributes independently
        assert result.bytes == 160

    def test_continues_after_failed_file(self, tmp_path: Path) -> None:
        # Given a missing file followed by a valid file
        failed = tmp_path / "missing.log"

        valid = tmp_path / "valid.log"
        valid.write_text(LogRow().to_line(), encoding="utf-8")
        service = LogAnalyzerService()

        # When processing both files
        result = service.analyze([failed, valid], bytes_exchanged=True)

        # Then processing continues and the missing file is counted as failed
        assert result.bytes == 110
        assert service.metrics.failed_files == 1
