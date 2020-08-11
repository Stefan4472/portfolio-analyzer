import datetime
import enum
import typing
import pathlib
import json
import dataclasses as dc


class TransactionType(enum.Enum):
    BUY = 1
    SELL = 2


@dc.dataclass
class Transaction:
    type: TransactionType
    ticker: str
    date: datetime.datetime
    volume: int
    price_per_share: float


def parse_transaction_file(
        filepath: pathlib.Path,
) -> typing.List[Transaction]:
    transactions: typing.List[Transaction] = []
    with open(filepath, 'r') as transaction_file:
        line_num = 0
        for line in transaction_file:
            line_num += 1
            type_str, ticker, date_str, volume_str, price_str = line.split()
            
            if type_str == 'BUY':
                t_type = TransactionType.BUY
            elif type_str == 'SELL':
                t_type = TransactionType.SELL
            else:
                raise ValueError(
                    'Invalid transaction type! (Line {}, col {})'.format(
                        line_num, 1)
                )

            date = datetime.datetime.strptime(date_str, r'%m/%d/%Y')
            volume = int(volume_str)
            price = float(price_str)

            transactions.append(Transaction(
                t_type,
                ticker,
                date,
                volume,
                price,
            ))
    return transactions


@dc.dataclass
class StockStatistic:
    quantity_bought: int = 0
    quantity_sold: int = 0
    first_buy: typing.Optional[datetime.datetime] = None
    last_sell: typing.Optional[datetime.datetime] = None
    starting_capital: float = 0.0
    ending_capital: float = 0.0

    def calc_abs_return(self) -> float:
        return self.ending_capital - self.starting_capital

    def calc_percent_return(self) -> float:
        return self.calc_abs_return() / self.starting_capital

    # NOTE: DOESN'T MAKE SENSE FOR THE TIMEFRAME OF MY INVESTMENTS
    # def calc_annualized_return(self) -> float:
    #     return 0.0  # TODO


# TODO: THIS CLASS ISN'T REALLY NECESSARY
class Portfolio:
    def __init__(
            self,
            transactions: typing.List[Transaction] = None,
    ):
        self.transactions = transactions if transactions else []
        # Set of stock tickers in the transactions
        self.stock_tickers: typing.Set[str] = set(t.ticker for t in transactions)
        self.per_stock_stats = self.calc_per_stock_stats()
        self.stats = self.calc_stats()

    # TODO: THESE SHOULD BE STAND-ALONE FUNCTIONS
    def calc_per_stock_stats(self) -> typing.Dict[str, StockStatistic]:
        per_stock_stats: typing.Dict[str, StockStatistic] = \
            {ticker: StockStatistic() for ticker in self.stock_tickers}
        for transaction in self.transactions:
            stock_stats = per_stock_stats[transaction.ticker]
            if transaction.type == TransactionType.BUY:
                stock_stats.quantity_bought += transaction.volume
                stock_stats.starting_capital += \
                    transaction.volume * transaction.price_per_share
                if stock_stats.first_buy is None:
                    stock_stats.first_buy = transaction.date
            elif transaction.type == TransactionType.SELL:
                stock_stats.quantity_sold += transaction.volume
                stock_stats.ending_capital += \
                    transaction.volume * transaction.price_per_share
                if stock_stats.last_sell is None:
                    stock_stats.last_sell = transaction.date
            else:
                raise ValueError('Programmer error: unsupported TransactionType')
            per_stock_stats[transaction.ticker] = stock_stats  # TODO: NECESSARY?
        return per_stock_stats

    def calc_stats(self) -> typing.Dict[str, typing.Any]:
        # TODO
        starting_capital: float = 0.0
        ending_capital: float = 0.0
        return {}

    def generate_plot_data(
            self,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            period: str = 'WEEK',
    ) -> typing.Dict[datetime.datetime, float]:
        for ticker in self.stock_tickers:
            fetch_stock_data(ticker, start_date, end_date)
        return {}


class StockDataPoint(typing.NamedTuple):
    date: datetime.datetime
    open_price: float
    close_price: float


def fetch_stock_data(
        ticker: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        write_to: typing.Optional[pathlib.Path] = None,
) -> typing.Dict[datetime.datetime, typing.Tuple[float, float]]:
    # TOOD: ENFORCE START_DATE, END_DATE ARE BOTH MONDAY?
    api_url = r'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={unix_start_time}&period2={unix_end_time}&interval=1wk&events=history'.format(
        ticker=ticker,
        unix_start_time=int(start_date.timestamp()),
        unix_end_time=int(end_date.timestamp()),
    )
    print(api_url)


transaction_file = 'transaction-test.txt'
transactions = parse_transaction_file(transaction_file)
print(transactions)
portfolio = Portfolio(transactions)
print(portfolio.stock_tickers)
print(portfolio.calc_per_stock_stats())
portfolio.generate_plot_data(
    start_date=datetime.datetime(year=2020, month=3, day=10),
    end_date=datetime.datetime(year=2020, month=5, day=1),
)