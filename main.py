import os
import datetime
import typing
import click
import pathlib
import json
import collections
from matplotlib import pyplot as plt
import transactions as tr
import stock_data as sd
import analyze as an
import plot



@click.command()
@click.argument('starting_cash', type=float)
@click.argument('transaction_files', type=click.Path(exists=True, readable=True), nargs=-1)
@click.option('-s', '--start_date', type=click.DateTime((r'%Y-%m-%d',)), required=True)
@click.option('-e', '--end_date', type=click.DateTime((r'%Y-%m-%d',)), required=True)
@click.option('--save_dir', type=click.Path(file_okay=False, dir_okay=True, writable=True), default=os.getcwd())
@click.option('--quiet', type=bool, default=False)
def run(
        starting_cash: float,
        transaction_files: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        save_dir: str,
        quiet: bool,
):
    """

    # TODO: A SIMPLE PORTFOLIO CLASS
    # TODO: INPUT TRANSACTIONS IN JSON FILE, THAT SPECIFIES THE NAME OF THE PORTFOLIO, AND THEN LIST OF TRANSACTIONS?
    # TODO: STATS.JSON OUTPUT WORKING
    # TODO: MAKE SURE USER DOESN'T GO BELOW $0 BALANCE OR 0 VOLUME ON ANY STOCK TRADE
    """
    if end_date <= start_date:
        raise ValueError('end_date must come chronologically after start_date')

    # Create save directory if it doesn't already exist
    save_path = pathlib.Path(save_dir)
    save_path.mkdir(exist_ok=True)
    # Convert each string path provided into a pathlib.Path object
    transaction_paths: typing.List[pathlib.Path] = \
        [pathlib.Path(path_str) for path_str in transaction_files]
    
    # Map filepath to list of transactions
    all_transactions: typing.Dict[pathlib.Path, typing.List[tr.Transaction]] = {}
    # Create set of all stock tickers required for analysis
    stock_tickers: typing.Set[str] = set()

    # Parse the transaction files, adding all found stock tickers to the set
    for file_path in transaction_paths:
        transaction_data = tr.parse_transaction_file(file_path)
        all_transactions[file_path] = transaction_data           
        stock_tickers |= tr.get_unique_tickers(transaction_data)

    # Create directory for stock data
    data_path = save_path / 'stock-data'
    data_path.mkdir(exist_ok=True)

    # Fetch data for the needed stock tickers and save to `data_path`
    stock_data = sd.fetch_all_data(
        stock_tickers,
        start_date,
        end_date,
        write_to_dir=data_path,
        quiet=quiet
    )

    # Map filepath to value-over-time OrderedDict
    all_vals_over_time: \
        typing.Dict[pathlib.Path, 'collections.OrderedDict[datetime.date, float]'] = {}

    # Calculate statistics for each transaction file
    for file_path, transactions in all_transactions.items():
        # Create save dir
        portfolio_path = save_path / file_path.stem
        portfolio_path.mkdir(exist_ok=True)

        stock_stats = an.calc_per_stock_stats(
            transactions,
            stock_data,
            start_date.date(),
            end_date.date(),
        )
        # Print stats to console.
        print('Stock Stats')
        for ticker, stats in stock_stats.items():
            print('{}: {}'.format(ticker, stats))
        # Write to file
        with open(portfolio_path / 'stats.json', 'w') as out_file:
            out_file.write('Hello world')
            # json.dump(stock_stats, out_file, indent=4, default=str)

        # Calculate portfolio value for every day between `start_date` and
        # `end_date`, inclusive
        val_over_time = an.calc_value_over_time(
            starting_cash,
            transactions,
            stock_data,
            start_date.date(),
            end_date.date(),
        )

        # Write out value-over-time
        out_path = pathlib.Path(portfolio_path) / (file_path.stem + '.csv')
        with open(out_path, 'w') as vals_out:
            vals_out.write('Date,Value at Close ($)\n')
            for date, value in val_over_time.items():
                vals_out.write('{},{}\n'.format(date, value))

        # Add to mapping
        all_vals_over_time[file_path] = val_over_time

        # Draw and save plot
        fig, ax = plot.create_portfolio_plot(
            starting_cash,
            all_vals_over_time,
            set([file_path,]),
        )
        fig.savefig(pathlib.Path(portfolio_path) / (file_path.stem + '.jpg'), bbox_inches='tight')

    fig, ax = plot.create_portfolio_plot(
        starting_cash,
        all_vals_over_time,
        all_vals_over_time.keys()
    )
    fig.savefig(pathlib.Path(save_dir) / 'portfolio-comparison.jpg', bbox_inches='tight')


if __name__ == '__main__':
    run()
