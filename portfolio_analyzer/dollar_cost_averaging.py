import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set

from finance_cache.finance_cache import FinanceCache, PriceHistory
from portfolio import Action, ActionType, Portfolio, PortfolioSchema


@dataclass
class DcaBuy:
    """
    Represents a scheduled purchase of a single stock for a Dollar-Cost-
    Averaged portfolio.
    """

    ticker: str
    amount_usd: float


@dataclass
class DollarCostAverageStrategy:
    """Representation of an automated portfolio that uses Dollar Cost Averaging."""

    # TODO: need a more general-purpose way of representing time periods, e.g.
    # "Every week on Monday", "Every 3 weeks on Tuesday", "On the 15th of each month".
    frequency: str
    orders: List[DcaBuy]

    def tickers(self) -> Set[str]:
        return set([buy.ticker for buy in self.orders])


def get_closest_following_monday(day: date) -> date:
    """
    Returns the Monday closest to `day` that comes on or after `day`.
    I.e., if `day` is itself a Monday, it will simply be returned as-is.
    """
    weekday = day.weekday()
    # Monday = 0
    if weekday == 0:
        return day
    return day + timedelta(days=7 - weekday)


def generate_portfolio(
    strategy: DollarCostAverageStrategy,
    start_date: date,
    end_date: date,
    finance_cache: FinanceCache,
) -> Portfolio:
    """
    Procedurally generates transactions based on the given strategy, running
    from `start_date` (inclusive) until `end_date` (exclusive).
    """
    # Note: for now we ignore `frequency` and always buy once a week on Monday.
    # If we don't have ticker data for that day, we try the following day.
    # If that also fails then we fail the overall attempt.
    cash_needed = 0
    actions: List[Action] = []
    curr_date = get_closest_following_monday(start_date)
    # TODO: get all needed tickers and pre-load them from the cache.
    # Prefetch the values of each ticker for the desired date range.
    price_history: Dict[str, Dict[date, PriceHistory]] = {}
    for ticker in strategy.tickers():
        if not finance_cache.knows_ticker(ticker):
            raise ValueError(f"finance_cache does not have data for {ticker}")
        price_history[ticker] = finance_cache.get_price_history(
            ticker, start_date, end_date
        )

    while curr_date < end_date:
        # For each scheduled buy, use the open price to create the action with
        # the proper price and number of shares.
        for order in strategy.orders:
            try:
                open_price = price_history[order.ticker][curr_date].open
                actions.append(
                    Action(
                        ActionType.Buy,
                        order.ticker,
                        curr_date,
                        order.amount_usd / open_price,
                        open_price,
                    )
                )
                cash_needed += order.amount_usd
            except KeyError as e:
                # TODO: find the next available day.
                print(f"Skipping {curr_date}.")
        curr_date += timedelta(weeks=1)

    return Portfolio(cash_needed, actions)


if __name__ == "__main__":
    cache = FinanceCache(
        Path(r"C:\Users\Stefan\Github\portfolio-analyzer\cache")
    )
    spec = DollarCostAverageStrategy("weekly", [DcaBuy("VGT", 500)])
    generated = generate_portfolio(spec, date(2022, 1, 1), date(2023, 1, 1), cache)
    # print(generated)
    with open("dcs.json", "w+") as out:
        json.dump(PortfolioSchema().dump(generated), out, indent=4)
