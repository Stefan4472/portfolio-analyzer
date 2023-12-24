import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set

from finance_cache.finance_cache import FinanceCache
from finance_cache.public_models import PriceHistory

from portfolio_analyzer.portfolio import Action, ActionType, Portfolio


@dataclass
class ProcessedPortfolio:
    # TODO: make immutable.
    tickers: Set[str]
    actions: List[Action]


def preprocess_portfolio(portfolio: Portfolio) -> ProcessedPortfolio:
    # TODO: check that each ticker is present in the cache?
    return ProcessedPortfolio(
        set([action.ticker for action in portfolio.actions]),
        sorted(portfolio.actions, key=lambda a: a.date),
    )


@dataclass
class DateAndValue:
    date: datetime.date
    value: float


def calculate_value_at_close(
    curr_holdings: Dict[str, float],
    date: datetime.date,
    price_history: Dict[str, Dict[datetime.date, PriceHistory]],
) -> float:
    """
    Returns the value of `curr_holdings` at the close of `date`.

    Raises ValueError if `price_history` does not have a value for
    every ticker on `date`.
    """
    curr_value = 0
    for ticker, volume in curr_holdings.items():
        if ticker not in price_history:
            raise ValueError(f"No data for {ticker}.")
        if date not in price_history[ticker]:
            raise ValueError(f"No data for {ticker} on {date}.")
        curr_value += volume * price_history[ticker][date].close
    return curr_value


def calculate_value_over_time(
    portfolio: ProcessedPortfolio,
    starting_cash: float,
    start_date: datetime.date,
    end_date: datetime.date,
    finance_cache: FinanceCache,
) -> List[DateAndValue]:
    """
    Calculates the value of the portfolio at every trading day between
    `start_date` and `end_date`, inclusive.

    Drops dates for which it does not have a stock price for every ticker.
    """
    # Silently correct the easy-to-make error of passing in a datetime.
    if isinstance(start_date, datetime.datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime.datetime):
        end_date = end_date.date()

    # Prefetch the values of each ticker for the desired date range.
    price_history: Dict[str, Dict[datetime.date, PriceHistory]] = {}
    for ticker in portfolio.tickers:
        if not finance_cache.knows_ticker(ticker):
            raise ValueError(f"finance_cache does not have data for {ticker}")
        price_history[ticker] = finance_cache.get_price_history(
            ticker, start_date, end_date
        )

    value_over_time: List[DateAndValue] = []
    # Track current stock holdings: {ticker -> volume}.
    curr_holdings: Dict[str, float] = defaultdict(lambda: 0)
    # The cash balance from buying/selling shares. May go below zero.
    cash = starting_cash
    # Index of next action to be applied.
    next_index = 0
    # Date being processed.
    curr_date = start_date

    while curr_date <= end_date:
        # Apply any actions from this day.
        while (
            next_index < len(portfolio.actions)
            and portfolio.actions[next_index].date == curr_date
        ):
            action = portfolio.actions[next_index]
            print(f"Processing action {action} on {curr_date}.")
            if action.type == ActionType.Buy:
                curr_holdings[action.ticker] += action.volume
                cash -= action.volume * action.price
            elif action.type == ActionType.Sell:
                curr_holdings[action.ticker] -= action.volume
                cash += action.volume * action.price
            else:
                raise NotImplementedError()
            next_index += 1

        try:
            curr_value = cash + calculate_value_at_close(
                curr_holdings, curr_date, price_history
            )
            value_over_time.append(DateAndValue(curr_date, curr_value))
        except ValueError:
            print(f"Skipping {curr_date} because we don't have data for every ticker.")
            pass

        # Increment to the next day
        curr_date = curr_date + datetime.timedelta(days=1)

    return value_over_time
