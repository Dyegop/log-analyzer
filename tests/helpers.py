"""Small log fixtures for tests."""

from dataclasses import dataclass


@dataclass
class LogRow:
    """Describe raw log fields with valid defaults."""

    timestamp: str = "1000.0"
    header_bytes: str = "10"
    client_ip: str = "192.0.2.1"
    status: str = "TCP_MISS/200"
    response_bytes: str = "100"
    method: str = "GET"
    url: str = "https://example.com/resource"
    username: str = "-"
    destination: str = "DIRECT/203.0.113.1"
    content_type: str = "text/html"

    def to_line(self, delimiter: str = " ") -> str:
        """Build a ten-field log row followed by a newline."""
        return (
            delimiter.join(
                [
                    self.timestamp,
                    self.header_bytes,
                    self.client_ip,
                    self.status,
                    self.response_bytes,
                    self.method,
                    self.url,
                    self.username,
                    self.destination,
                    self.content_type,
                ]
            )
            + "\n"
        )
