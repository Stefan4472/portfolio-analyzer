from datetime import date

from finance_cache.public_models import PriceHistory
from sqlalchemy import Date, Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

    def __repr__(self) -> str:
        return f"Stock({self.ticker})"


class PriceHistoryModel(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(20))
    day: Mapped[date] = mapped_column(Date)
    # TODO: Store as int for precision.
    open: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)

    def to_price_history(self) -> PriceHistory:
        return PriceHistory(
            day=self.day,
            open=self.open,
            close=self.close,
        )

    def __repr__(self) -> str:
        return f"PriceHistory(id={self.id}, ticker={self.ticker}, day={self.day}, open={self.open}, close={self.close})"
