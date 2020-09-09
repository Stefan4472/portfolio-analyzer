import datetime
import typing
import pathlib
import time
import urllib.request
import collections
import transactions as t


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
    # Set `last_date` to whatever the final `prev_date` was
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
        quiet: bool = False,
) -> StockPriceHistory:
    """Fetch and parse data for the specified ticker. `end_date` inclusive!"""
    if not quiet:
        print('Fetching stock data for {}...'.format(ticker))
    # Add one day to the `end` date in order for the API to correctly return
    # result *up until* midnight on the next day.
    end_inclusive = end_date + datetime.timedelta(days=1)
    # Create url to download data from. Use Yahoo! public data.
    api_url = r'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={unix_start_time}&period2={unix_end_time}&interval=1d&events=history'.format(
        ticker=ticker,
        unix_start_time=int(time.mktime(start_date.timetuple())),
        unix_end_time=int(time.mktime(end_inclusive.timetuple())),
    )
    # Download data to in-memory csv file
    with urllib.request.urlopen(api_url) as stock_file:
        return read_stock_datafile(
            stock_file, 
            needs_decode=True, 
            copy_to=write_to,
        )


class StockDataCache:
    """Note: Helper, but all data must be in `start_date`, `end_date`"""
    def __init__(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            write_to_dir: typing.Optional[pathlib.Path] = None,
            quiet: bool = False,
    ):
        self.start_date = start_date
        self.end_date = end_date
        self.write_to_dir = write_to_dir
        self.quiet = quiet
        self.cache: typing.Dict[str, StockPriceHistory] = {}

    def get_data(
            self,
            ticker: str,
    ) -> StockPriceHistory:
        if ticker not in self.cache:
            self.cache[ticker] = fetch_stock_data(
                ticker,
                self.start_date,
                self.end_date,
                write_to=self.write_to_dir / (ticker + '-data.csv') if self.write_to_dir else None,
                quiet=self.quiet,
            )
        return self.cache[ticker]

    def __getitem__(
            self, 
            key: str,
    ) -> StockPriceHistory:
        return self.get_data(key)