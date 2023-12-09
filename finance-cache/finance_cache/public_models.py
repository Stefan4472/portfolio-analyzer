from dataclasses import dataclass
from datetime import date


@dataclass
class PriceHistory:
    day: date
    open: float
    close: float
