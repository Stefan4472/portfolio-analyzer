import datetime
import typing
import collections
import dataclasses as dc
import transactions as t
import stock_data as sd


class StockStatistic(typing.NamedTuple):
    """Structure for storing the statistics for a specific stock
    holding (i.e., a single ticker) over a specific time period.
    """
    start_date: datetime.date
    end_date: datetime.date
    quantity_bought: int
    quantity_sold: int
    dollars_spent: float
    ending_capital: float
    absolute_return: float
    percent_return: float
    annualized_return: float

    def to_json(self) -> typing.Dict[str, typing.Any]:
        """Creates formatted json dictionary."""
        return {
            'shares_bought': self.quantity_bought,
            'shares_sold': self.quantity_sold,
            'dollars_spent': self.dollars_spent,
            'ending_capital': self.ending_capital,
            'absolute_return': self.absolute_return,
            'percent_return': self.percent_return,
            'annualized_return': self.annualized_return,
        }
    
    @staticmethod
    def create(
            start_date: datetime.date,
            end_date: datetime.date,
            quantity_bought: int,
            quantity_sold: int,
            dollars_spent: float,
            ending_capital: float,
    ) -> 'StockStatistic':
        """Factory method to create a `StockStatistic` instance. 
        
        Calculates and fills the returns for the stock holding.
        """
        # Calculate approximate number of years in question
        years_held = (end_date - start_date).days / 365
        # Calculate returns. Annualized formula from 
        # https://www.fool.com/knowledge-center/how-to-calculate-annualized-holding-period-return.aspx
        abs_return = ending_capital - dollars_spent
        frac_return = abs_return / dollars_spent
        annualized_return = \
            (1 + frac_return) ** (1 / years_held) - 1
        return StockStatistic(
            start_date,
            end_date,
            quantity_bought,
            quantity_sold,
            dollars_spent,
            ending_capital,
            abs_return,
            frac_return * 100,
            annualized_return,
        )


def calc_stock_statistic(
        ticker: str,
        starting_cash: float,
        transactions: typing.List[t.Transaction],
        start_date: datetime.date,
        end_date: datetime.date,
        stock_data_cache: sd.StockDataCache,
) -> StockStatistic:
    """Given a list of Transactions and a specified date range,
    calculate and return a `StockStatistic` instance.
    
    Note:
    - all transactions must be for the same, specified `ticker`
    - `start_date` and `end_date` are inclusive
    - `end_date` must be a valid trading day, and be represented in the 
      `stock_data` dict
    """
    quantity_bought = 0
    quantity_sold = 0
    dollars_invested = 0
    dollars_sold = 0

    for transaction in transactions:
        if transaction.ticker != ticker:
            raise ValueError('A transaction didn\'t match the specified ticker')
        # Ignore transactions that occurred outside the `start`-`end` window
        if transaction.date < start_date or transaction.date > end_date:
            continue
        if transaction.type == t.TransactionType.BUY:
            quantity_bought += transaction.volume
            dollars_invested += transaction.volume * transaction.price_per_share
            if dollars_invested > starting_cash:
                raise ValueError('Not enough money for transaction {}'.format(transaction))
        elif transaction.type == t.TransactionType.SELL:
            quantity_sold += transaction.volume
            dollars_sold += transaction.volume * transaction.price_per_share
            if quantity_sold > quantity_bought:
                raise ValueError('Not enough holdings to sell for transaction {}'.format(transaction))
        else:
            raise ValueError('Programmer error: unsupported TransactionType')
    
    # Calculate value of remaining holdings on `end_date`
    quantity_remaining = quantity_bought - quantity_sold
    value = stock_data_cache.get_data(ticker).history[end_date].close_price
    ending_capital = dollars_sold + quantity_remaining * value

    return StockStatistic.create(
        start_date,
        end_date,
        quantity_bought,
        quantity_sold,
        dollars_invested,
        ending_capital,
    )


def calc_per_stock_stats(
        transactions: typing.List[t.Transaction],
        starting_cash: float,
        start_date: datetime.date,
        end_date: datetime.date,
        stock_data_cache: sd.StockDataCache,
) -> typing.Dict[str, StockStatistic]:
    """Calculate the statistics for each stock ticker in the provided
    list of transactions.

    Returns a dictionary mapping stock ticker to `StockStatistic` 
    instance for that ticker.
    """
    # Map each ticker to a list of its transactions. Default to empty list.
    per_stock_transactions: \
        typing.Dict[str, typing.List[t.Transaction]] = collections.defaultdict(list)
    for transaction in transactions:
        per_stock_transactions[transaction.ticker].append(transaction)
    # Run `calc_stock_statistics` on each transaction list
    return {
        ticker: calc_stock_statistic(
            ticker,
            starting_cash,
            per_stock_transactions[ticker],
            start_date,
            end_date,
            stock_data_cache,
        ) for ticker in per_stock_transactions.keys()
    }


def calc_value_over_time(
        starting_cash: float,
        transactions: typing.List[t.Transaction],
        start_date: datetime.date,
        end_date: datetime.date,
        stock_data_cache: sd.StockDataCache,
) -> 'collections.OrderedDict[datetime.date, float]':
    """Calculates the value of the portfolio at every trading day between
    `start_date` and `end_date`, inclusive.

    NOTE: assumes `transactions` is sorted by date, ascending.
    This method is not hardened against missing/incomplete data.
    """
    # Map date to portfolio value. Dates will be indexed in ascending order.
    # By using the OrderedDict, we can then iterate over the keys in-order.
    val_over_time: 'collections.OrderedDict[datetime.date, float]' = {}
    # Cash-on-hand
    cash: float = starting_cash
    # Track current stock holdings: {ticker -> volume}. Default to zero.
    curr_holdings: typing.Dict[str, int] = collections.defaultdict(lambda: 0)
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

        # Calculate value of holdings at day close.
        # Ignore KeyErrors, which indicate that at least one of the stocks is 
        # missing data for this date (e.g., this date may be a weekend or
        # holiday).
        # NOTE: if the data is expected to be irregular, a better mechanism
        # for handling missing data will need to be developed.
        try:
            val_today = cash
            for ticker in curr_holdings:
                volume = curr_holdings[ticker]
                value = stock_data_cache.get_data(ticker).history[curr_date].close_price
                val_today +=  volume * value
            val_over_time[curr_date] = val_today
        except KeyError:
            pass

        # Increment to the next day
        curr_date += datetime.timedelta(days=1)
    return val_over_time