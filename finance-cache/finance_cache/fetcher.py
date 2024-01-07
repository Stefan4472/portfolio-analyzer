import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List

import requests
import yfinance
from pyrate_limiter import BucketFullException, Duration, Limiter, Rate


@dataclass
class StockInfo:
    """Information about a specific stock."""

    ticker: str
    name: str
    description: str
    quote_type: str


@dataclass
class DailyMarketData:
    """Market data for a single stock on a single day."""

    day: date
    open_price: float
    close_price: float


class MaxWaitExceeded(RuntimeError):
    """
    Error raised when the fetcher had to wait too long to perform an operation
    while waiting in order ot comply with the QPS limit.
    """

    pass


class YFinanceFetcher:
    """Fetches data from Yahoo! Finance, respecting a configured rate limit."""

    def __init__(
        self, max_qps=Rate(1, Duration.SECOND * 3), max_wait=timedelta(seconds=30)
    ):
        """
        Instantiate a fetcher.

        max_qps: The maximum rate at which the yfinance can be queried. This
          should be kept low in order to avoid being blocked by Yahoo.
        max_wait: The maximum time to wait for "permission" to send a request
          that respects `max_qps`.
        """
        self._limiter = Limiter(max_qps)
        self._acquire_timeout = max_wait

    def fetch_stock_info(self, ticker: str) -> StockInfo:
        """
        Fetches information about the specified `ticker` from Yahoo.

        Raises ValueError if no data could be fetched (i.e., the ticker is not
        known to Yahoo! Finance). Raises MaxWaitExceeded error if the request
        could not be made within the configured `max_wait`.
        """
        deadline = datetime.now() + self._acquire_timeout
        while datetime.now() < deadline:
            # Unfortunately the API does not provide a more elegant way to block.
            try:
                self._limiter.try_acquire("lock")
                yticker = yfinance.Ticker(ticker)
                return StockInfo(
                    ticker=yticker.info["symbol"],
                    name=yticker.info["shortName"],
                    description=yticker.info["longBusinessSummary"],
                    quote_type=yticker.info["quoteType"],
                )
            except BucketFullException:
                time.sleep(0.1)
            except requests.HTTPError:
                # yfinance raises a raw HTTPError 404 if the ticker is not
                # found.
                raise ValueError(f'Ticker "{ticker}" was not found.')
        raise MaxWaitExceeded(
            f"Waited for {self._acquire_timeout} to make a request that complies"
            f" with the configured yfinance rate limit."
        )

    def fetch_market_data(
        self, ticker: str, start_date: date, end_date: date
    ) -> List[DailyMarketData]:
        """
        Fetches market data (open/close prices) for the specified stock
        between `start_date` and `end_date` inclusive.

        Raises ValueError if no data could be fetched (i.e., the ticker is not
        known to Yahoo! Finance). Raises MaxWaitExceeded error if the request
        could not be made within the configured `max_wait`.
        """
        if start_date == end_date:
            return []
        deadline = datetime.now() + self._acquire_timeout
        while datetime.now() < deadline:
            try:
                self._limiter.try_acquire("lock")
                yticker = yfinance.Ticker(ticker)
                history = yticker.history(start=start_date, end=end_date)
                # Note: I added a filter to double-check we don't return data
                # outside [start_date, end_date]. I've noticed yfinance may
                # return data that is outside of the range by a day.
                return [
                    DailyMarketData(index.date(), row["Open"], row["Close"])
                    for index, row in history.iterrows()
                    if start_date <= index.date() <= end_date
                ]
            except BucketFullException:
                time.sleep(0.1)
            except requests.HTTPError:
                raise ValueError(f'Ticker "{ticker}" was not found.')
        raise MaxWaitExceeded(
            f"Waited for {self._acquire_timeout} to make a request that complies"
            f" with the configured yfinance rate limit."
        )
