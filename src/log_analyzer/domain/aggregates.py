from collections import Counter
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address

from log_analyzer.domain import AggregateResults, IPFrequency, LogRecord


class LogAggregates:
    """Incremental calculations for log records.

    IP frequencies combine client and destination occurrences. An IP appearing
    in both fields of a record counts twice; unavailable IP fields are skipped.
    """

    def __init__(
        self,
        *,
        mfip: bool = False,
        lfip: bool = False,
        eps: bool = False,
        bytes_exchanged: bool = False,
    ) -> None:
        """Select the calculations to aggregate from.

        Args:
            mfip: Calculate the most frequent IPs across both fields.
            lfip: Calculate the least frequent IPs across both fields.
            eps: Calculate the average events per second over the observed duration.
            bytes_exchanged: Sum response header and response byte counts.
        """
        self._mfip = mfip
        self._lfip = lfip
        self._eps = eps
        self._bytes_exchanged = bytes_exchanged

        self._ip_counts: Counter[IPv4Address | IPv6Address] = Counter()
        self._first_timestamp: Decimal | None = None
        self._last_timestamp: Decimal | None = None
        self._total_bytes: int = 0
        self._record_count: int = 0
        self._timestamp_count: int = 0

    def produce_results(self) -> AggregateResults:
        """Produce results for the selected operations.

        Returns:
            Selected results as an `AggregateResults` entity.

        Raises:
            ValueError: If no records have been accumulated.
        """
        if not self._record_count:
            raise ValueError("No records are available for analysis.")

        result: dict[str, object] = {}

        if self._mfip:
            result["mfip"] = self._frequency(self._ip_counts, most=True)
        if self._lfip:
            result["lfip"] = self._frequency(self._ip_counts, most=False)
        if self._eps:
            result["eps"] = self._events_per_second()
        if self._bytes_exchanged:
            result["bytes"] = self._total_bytes

        return AggregateResults.model_validate(result)

    def aggregate(self, record: LogRecord) -> None:
        """Update selected calculations independently using available fields."""

        if self._mfip or self._lfip:
            self._aggregate_ips(record)
        if self._bytes_exchanged:
            self._aggregate_bytes(record)
        if self._eps:
            self._aggregate_timestamps(record)

        self._record_count += 1

    def _aggregate_ips(self, record: LogRecord) -> None:
        """Count each available client and destination IP occurrence."""
        if record.client_ip:
            self._ip_counts[record.client_ip] += 1
        if record.destination_ip:
            self._ip_counts[record.destination_ip] += 1

    def _aggregate_bytes(self, record: LogRecord) -> None:
        """Sum available byte fields independently."""
        if record.response_header_bytes:
            self._total_bytes += record.response_header_bytes
        if record.response_bytes:
            self._total_bytes += record.response_bytes

    def _aggregate_timestamps(self, record: LogRecord) -> None:
        """Count timestamped events and record the given timestamp."""
        timestamp = record.timestamp
        if timestamp is None:
            return
        self._timestamp_count += 1
        if self._first_timestamp is None or timestamp < self._first_timestamp:
            self._first_timestamp = timestamp
        if self._last_timestamp is None or timestamp > self._last_timestamp:
            self._last_timestamp = timestamp

    def _events_per_second(self) -> float | None:
        """Return the average rate, or None when no positive duration exists."""

        if (
            self._first_timestamp is None
            or self._last_timestamp is None
            or self._first_timestamp == self._last_timestamp
        ):
            return None

        duration = self._last_timestamp - self._first_timestamp
        return float(self._timestamp_count / duration)

    @staticmethod
    def _frequency(counts: Counter[IPv4Address | IPv6Address], *, most: bool) -> list[IPFrequency]:
        """Select every IP tied at the requested frequency extreme.

        Args:
            counts: Combined client and destination IP occurrence counts.
            most: Select the maximum when true, otherwise the minimum.

        Returns:
            Tied IPs and counts, sorted by address string.
        """

        if not counts:
            return []

        result = max(counts.values()) if most else min(counts.values())

        return [
            IPFrequency(ip=ip_address, count=count)
            for ip_address, count in sorted(counts.items(), key=lambda item: str(item[0]))
            if count == result
        ]
