import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from finance_cache.config import CacheConfig, CacheConfigSchema
from finance_cache.fetcher import YFinanceFetcher
from finance_cache.models import Base, PriceHistoryModel, StockModel
from finance_cache.public_models import PriceHistory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


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
            find_stock = session.query(StockModel).filter(
                StockModel.ticker == ticker.upper()
            )
            return session.query(find_stock.exists()).scalar()

    def get_price_history(
        self, ticker: str, start_date: date, end_date: date
    ) -> Dict[date, PriceHistory]:
        """
        Returns price history from `start_date` inclusive until `end_date`
        inclusive for the specified ticker, ordered by date increasing.
        """
        with self._session_maker() as session:
            res = (
                session.query(PriceHistoryModel)
                .join(StockModel)
                .where(StockModel.ticker == ticker)
                .where(PriceHistoryModel.stock_id == StockModel.id)
                .where(PriceHistoryModel.day >= start_date)
                .where(PriceHistoryModel.day <= end_date)
                .order_by(PriceHistoryModel.day)
                .all()
            )
            if res:
                return {r.day: r.to_price_history() for r in res}
        raise ValueError(f"No data for {ticker}.")

    def load(self, ticker: str):
        """Loads data for the specified stock into the cache. This is slow."""
        print(f"Loading data for {ticker}.")
        session: Session
        with self._session_maker() as session:
            stock: Optional[StockModel] = (
                session.query(StockModel).filter(StockModel.ticker == ticker).first()
            )
            if not stock:
                # Load information about the stock.
                stock_info = self._fetcher.fetch_stock_info(ticker)
                stock = StockModel(
                    ticker=ticker,
                    name=stock_info.name,
                    quote_type=stock_info.quote_type,
                    description=stock_info.description,
                )
                session.add(stock)
                # Flush to ensure `stock` gets an ID primary key assigned.
                session.flush()

            # Don't fetch data for days that we already have in the database.
            freshest_market_data: Optional[PriceHistoryModel] = (
                session.query(PriceHistoryModel)
                .where(PriceHistoryModel.stock_id == stock.id)
                .order_by(PriceHistoryModel.day.desc())
                .first()
            )
            start_date = (
                freshest_market_data.day + timedelta(days=1)
                if freshest_market_data
                else self._config.history_start
            )

            market_data = self._fetcher.fetch_market_data(
                ticker, start_date, datetime.now().date()
            )
            for day in market_data:
                session.add(
                    PriceHistoryModel(
                        stock_id=stock.id,
                        day=day.day,
                        open=day.open_price,
                        close=day.close_price,
                    )
                )
            session.commit()
