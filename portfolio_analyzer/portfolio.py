from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from marshmallow import Schema, fields, post_load, validate
from marshmallow_enum import EnumField


class ActionType(Enum):
    """Represents a possible action taken."""

    Buy = "BUY"
    Sell = "SELL"


@dataclass
class Action:
    """Represents a financial action taken, e.g. a stock buy or sell."""

    type: ActionType
    ticker: str
    date: datetime.date
    volume: float
    price: Optional[float]


@dataclass
class Portfolio:
    """A simple representation of a user-defined portfolio."""

    starting_cash: float
    actions: List[Action]


class ActionSchema(Schema):
    """The schema for an Action."""

    type = EnumField(ActionType, allow_none=False)
    ticker = fields.Str(allow_none=False)
    date = fields.Date(format="%Y-%m-%d", allow_none=False)
    volume = fields.Float(allow_none=False)
    price = fields.Float(required=False, allow_none=False)


class PortfolioSchema(Schema):
    """The schema for a Portfolio."""

    starting_cash = fields.Float(
        required=True, allow_none=False, validate=validate.Range(min=0)
    )
    actions = fields.List(fields.Nested(ActionSchema))

    @post_load
    def to_dataclass(self, data, **kwargs) -> Portfolio:
        return Portfolio(data["starting_cash"], [Action(**a) for a in data["actions"]])
