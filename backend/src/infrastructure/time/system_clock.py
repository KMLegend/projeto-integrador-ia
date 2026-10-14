from datetime import UTC, datetime

from domain.ports.clock import Clock


class SystemClock(Clock):
    """Implementacao de Clock baseada no relogio UTC do sistema operacional."""

    def now(self) -> datetime:
        return datetime.now(UTC)
