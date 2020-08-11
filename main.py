import datetime
import enum
import typing
import pathlib
import urllib.request
import collections
import json
import matplotlib.pyplot as plt
import dataclasses as dc


class TransactionType(enum.Enum):
    BUY = 1
    SELL = 2


@dc.dataclass
class Transaction:
    type: TransactionType
    ticker: str
    date: datetime.date
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

            date = datetime.datetime.strptime(date_str, r'%m/%d/%Y').date()
            volume = int(volume_str)
            price = float(price_str)

            transactions.append(Transaction(
                t_type,
                ticker,
                date,
                volume,
                price,
            ))
    # Sort by date, ascending
    transactions.sort(key=lambda t: t.date)
    return transactions


@dc.dataclass
class StockStatistic:
    quantity_bought: int = 0
    quantity_sold: int = 0
    first_buy: typing.Optional[datetime.date] = None
    last_sell: typing.Optional[datetime.date] = None
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
        # self.stats = self.calc_stats()

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

    # def calc_stats(self) -> typing.Dict[str, typing.Any]:
    #     # TODO
    #     starting_capital: float = 0.0
    #     ending_capital: float = 0.0
    #     return {}

    # def generate_plot_data(
    #         self,
    #         start_date: datetime.datetime,
    #         end_date: datetime.datetime,
    #         period: str = 'WEEK',
    # ) -> typing.Dict[str, typing.List[StockDataPoint]]:
    #     """Returns dict of stock tickers to list of ordered StockDataPoint."""
    #     for ticker in self.stock_tickers:
    #         print(fetch_stock_data(ticker, start_date, end_date))
    #     return {}


class StockDataPoint(typing.NamedTuple):
    day: datetime.date
    open_price: float
    close_price: float


class StockPriceHistory(typing.NamedTuple):
    start_date: datetime.date
    end_date: datetime.date
    history: 'collections.OrderedDict[datetime.date, StockDataPoint]'

    
def read_stock_datafile(
        filehandle: typing.IO,
        needs_decode: bool = False,
        copy_to: typing.Optional[pathlib.Path] = None,
) -> StockPriceHistory:
    """Read the provided file handle of csv stock data."""
    stock_data: 'collections.OrderedDict[datetime.date, StockDataPoint]' = \
        collections.OrderedDict()
    csv_data = filehandle.read().decode() if needs_decode else filehandle.read()
    line_number = 0
    first_date: typing.Optional[datetime.date] = None
    prev_date: typing.Optional[datetime.date] = None

    for line in csv_data.split('\n'):
        line_number += 1
        # Skip the first line (column names)
        if line_number == 1:
            continue
        else:   
            cols = line.split(',')
            # Parse date column
            date = datetime.datetime.strptime(cols[0], r'%Y-%m-%d').date()
            
            # Initialize `first_date` on first line of data
            if line_number == 2:
                first_date = date

            # Ensure that data is in-order
            if prev_date and date <= prev_date:
                raise ValueError(
                    'Data error: out-of-order data (lines {}-{})'.format(
                        line_number - 1,
                        line_number,
                    ))
            # Initialize `prev_date` (will happen on first line of data)
            elif not prev_date:
                prev_date = date
                
            stock_data[date] = StockDataPoint(
                date,
                float(cols[1]),
                float(cols[4]),
            )
            prev_date = date

    last_date = prev_date

    # Optionally write the stock data to the provided file path
    if copy_to:
        with open(copy_to, 'w') as out_file:
            out_file.write(csv_data)

    return StockPriceHistory(
        first_date, 
        last_date, 
        stock_data,
    )


def fetch_stock_data(
        ticker: str,
        start_date: datetime.date,
        end_date: datetime.date,
        write_to: typing.Optional[pathlib.Path] = None,
) -> typing.List[StockDataPoint]:
    # Create url to download data from. Use Yahoo! public data.
    api_url = r'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={unix_start_time}&period2={unix_end_time}&interval=1d&events=history'.format(
        ticker=ticker,
        unix_start_time=int(start_date.timestamp()),
        unix_end_time=int(end_date.timestamp()),
    )
    # Download data to in-memory csv file
    with urllib.request.urlopen(api_url) as stock_file:
        return read_stock_datafile(
            stock_file, 
            needs_decode=True, 
            copy_to=write_to,
        )


def calc_value_over_time(
        transactions: typing.List[Transaction],
        stock_data: typing.Dict[str, typing.List[StockDataPoint]],
        start_date: datetime.date,
        end_date: datetime.date,
) -> 'collections.OrderedDict[datetime.date, float]':
    """NOTE: assumes `transactions` is sorted. `end_date` is inclusive!
    This method is not hardened against missing/incomplete data."""
    val_over_time: 'collections.OrderedDict[datetime.date, float]' = {}
    # Value of sold stocks
    running_gain: float = 0
    # Track current holdings: {ticker -> volume}
    curr_holdings: typing.Dict[str, float] = {}
    # Index of next transaction to be applied
    next_transaction_index = 0

    money_in: float = 0
    money_out: float = 0
    
    curr_date = start_date

    while curr_date <= end_date:
        # Apply any transactions from this day
        while next_transaction_index < len(transactions) and \
                transactions[next_transaction_index].date == curr_date:
            apply_transaction = transactions[next_transaction_index]
            ticker = apply_transaction.ticker

            # Set holdings to zero (TODO: THIS IS ANNOYING, USE A DEFAULTDICT OR SOMETHING)
            if apply_transaction.ticker not in curr_holdings:
                curr_holdings[ticker] = 0
            
            if apply_transaction.type == TransactionType.BUY:
                curr_holdings[ticker] += apply_transaction.volume
                # running_gain -= apply_transaction.volume * apply_transaction.price_per_share
                money_in += apply_transaction.volume * apply_transaction.price_per_share

            else:
                curr_holdings[ticker] -= apply_transaction.volume
                # cash += apply_transaction.volume * apply_transaction.price_per_share
                money_out += apply_transaction.volume * apply_transaction.price_per_share

            next_transaction_index += 1

        try:
            # Calculate value of holdings at day close
            close_value = \
                sum(volume * stock_data[ticker].history[curr_date].close_price \
                        for ticker, volume in curr_holdings.items())
            print('{}, {}'.format(curr_date, close_value))
            val_over_time[curr_date] = close_value
        # Ignore dates that are missing data (e.g. weekends)
        except KeyError:
            pass
        curr_date += datetime.timedelta(days=1)
    return val_over_time
    

if __name__ == '__main__':
    transaction_file = 'transaction-test.txt'
    transactions = parse_transaction_file(transaction_file)
    print(transactions)
    # portfolio = Portfolio(transactions)
    # print(portfolio.stock_tickers)
    # print(portfolio.calc_per_stock_stats())
    # data = fetch_stock_data(
    #     'NFLX',
    #     datetime.date(year=2020, month=3, day=10),
    #     datetime.date(year=2020, month=5, day=2),
    #     write_to='nflx-data.csv',
    # )
    stock_data = {}
    with open('nflx-data.csv', 'r') as data_file:
        stock_data['NFLX'] = read_stock_datafile(data_file)
    with open('aapl-data.csv', 'r') as data_file:
        stock_data['AAPL'] = read_stock_datafile(data_file)
    val_over_time = calc_value_over_time(
        transactions,
        stock_data,
        datetime.date(year=2020, month=3, day=10),
        datetime.date(year=2020, month=5, day=2),
    )
    # Plotting
    fig, ax = plt.subplots()
    fig.suptitle('Portfolio Value Over Time')
    ax.plot(val_over_time.keys(), val_over_time.values())
    # ax.plot(stock_data['NFLX'].history.keys(), [s.open_price for s in stock_data['NFLX'].history.values()])
    plt.show()
