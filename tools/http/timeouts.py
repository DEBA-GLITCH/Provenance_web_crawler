# tools/http/timeouts.py

from dataclasses import dataclass

@dataclass(frozen=True)
class TimeoutConfig:
    """
    Explicit timeout policy.
    Encodes system patience.
    """
    connect_timeout: float = 5.0
    read_timeout: float = 10.0
    total_deadline: float = 20.0
