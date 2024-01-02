import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict

from finance_cache.config import CacheConfig, CacheConfigSchema
from finance_cache.fetcher import YFinanceFetcher
from finance_cache.models import Base, PriceHistoryModel, TickerModel
from finance_cache.public_models import PriceHistory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class FinanceCache:

    # TODO: allow injecting a logger?
    def __init__(self, base_path: Path):
        """
        Connects to the FinanceCache instance at the specified base directory.

        The FinanceCache must have been previously created via
        `FinanceCache.create()`.
        """
        if not base_path.exists():
            raise ValueError(f"The provided path does not exist: {base_path}.")
        if not base_path.is_dir():
            raise ValueError(f"The provided path must be a directory: {base_path}.")

        db_path = self._make_db_path(base_path)
        if not db_path.exists():
            raise ValueError(
                f"Could not find a database in the directory. "
                f"Expected to find one at {db_path}."
            )

        config_path = self._make_config_path(base_path)
        if not config_path.exists():
            raise ValueError(
                f"Could not find a config file in the directory. "
                f"Expected to find one at {config_path}."
            )

        with open(config_path) as cfg_file:
            self._config = CacheConfigSchema().load(json.load(cfg_file))

        self._engine = create_engine(f"sqlite:///{db_path}")
        self._session_maker = sessionmaker(bind=self._engine)
        self._fetcher = YFinanceFetcher()

    @staticmethod
    def create(base_path: Path, config: CacheConfig):
        """
        Creates a FinanceCache instance in the specified directory with the
        desired options.
        """
        if base_path.exists():
            raise ValueError(f"cache_path must not already exist: {base_path}.")
        errors = CacheConfigSchema().validate(CacheConfigSchema().dump(config))
        if errors:
            raise ValueError(f"The provided config has the following issues: {errors}")
        base_path.mkdir()

        # Create database.
        engine = create_engine(
            f"sqlite:///{FinanceCache._make_db_path(base_path).absolute()}"
        )
        Base.metadata.create_all(engine)

        # Write out config.
        with open(FinanceCache._make_config_path(base_path), "w+") as out:
            json.dump(CacheConfigSchema().dump(config), out, indent=4)

    @staticmethod
    def _make_db_path(base_path: Path) -> Path:
        """Returns the path to where the Sqlite file is expected. `base_path` is the FinanceCache instance directory."""
        return base_path / "finance_cache.sqlite"

    @staticmethod
    def _make_config_path(base_path: Path) -> Path:
        """Returns the path to where the config file is expected. `base_path` is the FinanceCache instance directory."""
        return base_path / "config.json"

    def knows_ticker(self, ticker: str) -> bool:
        with self._session_maker() as session:
            find_ticker = session.query(TickerModel).filter(
                TickerModel.ticker == ticker.upper()
            )
            return session.query(find_ticker.exists()).scalar()

    def get_price_history(
        self, ticker: str, start_date: date, end_date: date
    ) -> Dict[date, PriceHistory]:
        """
        Returns price history from `start_date` inclusive until `end_date`
        inclusive for the specified ticker, ordered by date increasing.
        """
        with self._session_maker() as session:
            find_ticker = (
                session.query(TickerModel).filter(TickerModel.ticker == ticker).first()
            )
            if find_ticker is None:
                raise ValueError(f"No such ticker in cache.")

            return {
                r.day: r.to_price_history()
                for r in session.query(PriceHistoryModel)
                .where(PriceHistoryModel.ticker == ticker)
                .where(PriceHistoryModel.day >= start_date)
                .where(PriceHistoryModel.day <= end_date)
                .order_by(PriceHistoryModel.day)
                .all()
            }

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
                self._config.history_start,
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
