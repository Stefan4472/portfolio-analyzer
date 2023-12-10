from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List

from finance_cache.fetcher import YFinanceFetcher
from finance_cache.models import Base, PriceHistoryModel, TickerModel
from finance_cache.public_models import PriceHistory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class FinanceCache:
    # TODO: allow injecting a logger?
    # TODO: some common way of storing/loading a config for use with batch programs.
    def __init__(self, cache_path: Path, history_start: date):
        """
        Construct a FinanceCache instance with an underlying SQLite database.

        cache_path: path to a directory where this instance can persist data.
            If the path does not exist, then a directory will be created.
        history_start: the earliest date that market data will be stored from.
            For example, if set to 2020-01-01, then the cache will not retrieve
            any market data from dates earlier than January 1st, 2020.
        """
        if cache_path.exists() and not cache_path.is_dir():
            raise ValueError(f"cache_path must be a directory: {cache_path}")
        cache_path.mkdir(exist_ok=True)
        self._db_path = cache_path / "finance_cache.sqlite"
        self._engine = create_engine(f"sqlite:///{self._db_path.absolute()}")
        self._session_maker = sessionmaker(bind=self._engine)
        self._history_start = history_start
        self._fetcher = YFinanceFetcher()
        Base.metadata.create_all(self._engine)

    def get_price_history(self, ticker: str) -> List[PriceHistory]:
        """Returns all known price history for the specified ticker."""
        with self._session_maker() as session:
            find_ticker = (
                session.query(TickerModel).filter(TickerModel.ticker == ticker).first()
            )
            if find_ticker is None:
                raise ValueError(f"No such ticker in cache.")

            res = (
                session.query(PriceHistoryModel)
                .filter(PriceHistoryModel.ticker == ticker)
                .order_by(PriceHistoryModel.day)
                .all()
            )
            return [r.to_price_history() for r in res]

    def load(self, ticker: str):
        """Loads data for the specified ticker into the cache. This is slow."""
        self._fetch_data(ticker)

    def _fetch_data(self, ticker: str):
        """
        Fetches data from the external source and writes it to the database.

        This is very slow.
        """
        print(f"Fetching data for {ticker}.")
        with self._session_maker() as session:
            find_ticker = (
                session.query(TickerModel).filter(TickerModel.ticker == ticker).first()
            )
            # TODO: load date between `last_fetch` and now.
            if find_ticker:
                print(f"We already have data for {ticker}.")
                return
            ticker_data = self._fetcher.fetch(
                ticker,
                self._history_start,
                datetime.now().date(),
                datetime.now() + timedelta(seconds=10),
            )
            # TODO: look into settings to optimize bulk adds
            session.add(TickerModel(ticker=ticker))
            for index, row in ticker_data.price_history.iterrows():
                session.add(
                    PriceHistoryModel(
                        ticker=ticker,
                        day=index.date(),
                        open=row["Open"],
                        close=row["Close"],
                    )
                )
            session.commit()
