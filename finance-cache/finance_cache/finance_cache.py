from pathlib import Path
from typing import List

import yfinance
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from finance_cache.models import Base, PriceHistoryModel, TickerModel
from finance_cache.public_models import PriceHistory


class FinanceCache:
    # TODO: allow injecting a logger?
    def __init__(self, cache_path: Path):
        if cache_path.exists() and not cache_path.is_dir():
            raise ValueError(f"cache_path must be a directory: {cache_path}")
        cache_path.mkdir(exist_ok=True)
        self._db_path = cache_path / "finance_cache.sqlite"
        self._engine = create_engine(f"sqlite:///{self._db_path.absolute()}", echo=True)
        self._session_maker = sessionmaker(bind=self._engine)
        Base.metadata.create_all(self._engine)

    def get_price_history(self, ticker: str) -> List[PriceHistory]:
        """Returns all known price history for the specified ticker."""
        with self._session_maker() as session:
            find_ticker = (
                session.query(TickerModel).filter(TickerModel.ticker == ticker).first()
            )
            if find_ticker is None:
                self._fetch_data(ticker)
            res = (
                session.query(PriceHistoryModel)
                .filter(PriceHistoryModel.ticker == ticker)
                .order_by(PriceHistoryModel.day)
                .all()
            )
            return [r.to_price_history() for r in res]

    def _fetch_data(self, ticker: str):
        """Fetches data from YFinance and writes it to the database."""
        print(f"Fetching data for {ticker}.")
        yticker = yfinance.Ticker(ticker)
        price_history = yticker.history(period="1mo")
        # TODO: look into settings to optimize bulk adds
        with self._session_maker() as session:
            session.add(TickerModel(ticker=ticker))
            for index, row in price_history.iterrows():
                session.add(
                    PriceHistoryModel(
                        ticker=ticker,
                        day=index.date(),
                        open=row["Open"],
                        close=row["Close"],
                    )
                )
            session.commit()
