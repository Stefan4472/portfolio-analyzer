import datetime
import enum
import typing
import pathlib
import dataclasses as dc


class TransactionType(enum.Enum):
    BUY = 1
    SELL = 2


@dc.dataclass
class Transaction:
    """Represents a buy/sell transaction of a certain volume of a certain 
    ticker."""
    type: TransactionType
    ticker: str
    date: datetime.date
    volume: int
    price_per_share: float
