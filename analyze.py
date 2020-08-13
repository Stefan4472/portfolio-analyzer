import datetime
import typing
import collections
import dataclasses as dc
import transactions as t
import stock_data as sd


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
            transactions: typing.List[t.Transaction] = None,
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
            if transaction.type == t.TransactionType.BUY:
                stock_stats.quantity_bought += transaction.volume
                stock_stats.starting_capital += \
                    transaction.volume * transaction.price_per_share
                if stock_stats.first_buy is None:
                    stock_stats.first_buy = transaction.date
            elif transaction.type == t.TransactionType.SELL:
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





def calc_value_over_time(
        starting_cash: float,
        transactions: typing.List[t.Transaction],
        stock_data: typing.Dict[str, typing.List[sd.StockDataPoint]],
        start_date: datetime.date,
        end_date: datetime.date,
) -> 'collections.OrderedDict[datetime.date, float]':
    """NOTE: assumes `transactions` is sorted. `end_date` is inclusive!
    This method is not hardened against missing/incomplete data."""
    # Map date to portfolio value. Dates will be indexed in ascending order.
    # By using the OrderedDict, we can then iterate over the keys in-order.
    val_over_time: 'collections.OrderedDict[datetime.date, float]' = {}
    # Cash-on-hand
    cash: float = starting_cash
    # Track current stock holdings: {ticker -> volume}. Default to zero.
    curr_holdings: typing.Dict[str, float] = collections.defaultdict(lambda: 0)
    # Index of next transaction to be applied
    next_transaction_index = 0
    # Date being analyzed
    curr_date = start_date

    while curr_date <= end_date:
        # Apply any transactions from this day
        while next_transaction_index < len(transactions) and \
                transactions[next_transaction_index].date == curr_date:
            apply_transaction = transactions[next_transaction_index]
            ticker = apply_transaction.ticker

            if apply_transaction.type == t.TransactionType.BUY:
                curr_holdings[ticker] += apply_transaction.volume
                cash -= apply_transaction.volume * apply_transaction.price_per_share
            elif apply_transaction.type == t.TransactionType.SELL:
                curr_holdings[ticker] -= apply_transaction.volume
                cash += apply_transaction.volume * apply_transaction.price_per_share
            else:
                raise ValueError('Programmer Error: Unsupported TransactionType')
            next_transaction_index += 1

        # Calculate value of holdings at day close
        try:
            close_value = cash + \
                sum(volume * stock_data[ticker].history[curr_date].close_price \
                        for ticker, volume in curr_holdings.items())
            val_over_time[curr_date] = close_value
        # Ignore KeyErrors, which indicate that at least one of the stocks is 
        # missing data for this date (e.g. on a weekend).
        # NOTE: if the data is expected to be irregular, a better mechanism
        # for handling missing data will need to be developed.
        except KeyError:
            pass

        # Increment to the next day
        curr_date += datetime.timedelta(days=1)
    return val_over_time