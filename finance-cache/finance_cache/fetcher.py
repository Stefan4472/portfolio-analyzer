import time
from dataclasses import dataclass
from datetime import date, datetime

import yfinance
from pandas import DataFrame
from pyrate_limiter import BucketFullException, Duration, Limiter, Rate


@dataclass
class TickerData:
    """All data fetched for a specific ticker."""

    ticker: str
    price_history: DataFrame


class YFinanceFetcher:
    """Fetches data from Yahoo! Finance, respecting a configured rate limit."""

    def __init__(self, cool_off_seconds: int = 3):
        self._limiter = Limiter(Rate(1, Duration.SECOND * cool_off_seconds))

    def fetch(
        self, ticker: str, start: date, end: date, max_deadline: datetime
    ) -> TickerData:
        print(f"Fetching {ticker} from {start} to {end}.")
        # Unfortunately the API does not provide a more elegant way to block.
        while datetime.now() < max_deadline:
            try:
                self._limiter.try_acquire("lock")
                yticker = yfinance.Ticker(ticker)
                price_history = yticker.history(start=start, end=end)
                return TickerData(ticker=ticker, price_history=price_history)
            except BucketFullException:
                time.sleep(0.1)
