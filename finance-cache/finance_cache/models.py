from datetime import date
from typing import List

from finance_cache.public_models import PriceHistory
from sqlalchemy import Date, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class StockModel(Base):
    """Information known about a single stock."""

    __tablename__ = "stock"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    quote_type: Mapped[str] = mapped_column(String(25))
    description: Mapped[str] = mapped_column(String())

    # MarketData records associated with this stock.
    market_data: Mapped[List["MarketDataModel"]] = relationship()

    def __repr__(self) -> str:
        return f"Stock({self.ticker})"


class MarketDataModel(Base):
    """Market data for a single stock on a particular day."""

    __tablename__ = "market_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    # The stock that this record describes.
    stock_id: Mapped[int] = mapped_column(ForeignKey("stock.id"))
    day: Mapped[date] = mapped_column(Date)
    # TODO: Store as int for precision.
    open_price: Mapped[float] = mapped_column(Float)
    close_price: Mapped[float] = mapped_column(Float)

    # There must only be one record per ticker for any given day.
    __table_args__ = (UniqueConstraint("stock_id", "day"),)

    def to_price_history(self) -> PriceHistory:
        return PriceHistory(
            day=self.day,
            open=self.open_price,
            close=self.close_price,
        )

    def __repr__(self) -> str:
        return (
            f"PriceHistory(id={self.id}, ticker_id={self.stock_id}, "
            f"day={self.day}, open={self.open_price}, close={self.close_price})"
        )
