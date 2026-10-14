from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Porta para obtencao de data e hora atual do sistema."""

    def now(self) -> datetime:
        """Retorna o timestamp atual em UTC."""
        ...
