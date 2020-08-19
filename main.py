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
@click.argument('transaction_file')
@click.argument('save_dir', type=click.Path())
@click.option('-s', '--start_date', type=click.DateTime((r'%Y-%m-%d',)))
@click.option('-e', '--end_date', type=click.DateTime((r'%Y-%m-%d',)))
@click.option('-h', '--hypotheticals', type=click.Path(exists=True), multiple=True)
def run(
        starting_cash: float,
        transaction_file: str,
        save_dir: str = None,
        start_date: datetime.datetime = None,
        end_date: datetime.datetime = None,
        hypotheticals: typing.Tuple[str] = None,
):
    """
    Note: ideally, we would make '-s' AND '-e' required, or neither.
    """
    # Require either `start_date` AND `end_date` to be defined, or neither
    if (start_date and not end_date) or (end_date and not start_date):
        raise ValueError(
            'start_date and end_date must be both defined, or neither defined')

    # Parse transactions file
    transactions = tr.parse_transaction_file(pathlib.Path(transaction_file))

    # Default `start_date`, `end_date` to the first/last transactions
    start_date = start_date.date() if start_date else transactions[0].date
    end_date = end_date.date() if end_date else transactions[-1].date
    if start_date > end_date:
        raise ValueError('start_date must come chronologically before end_date')

    # Create save directory if it doesn't already exist
    pathlib.Path(save_dir).mkdir(exist_ok=True)

    # Create set of all stock tickers required for main + hypothetical analyses
    stock_tickers: typing.Set[str] = tr.get_unique_tickers(transactions)

    # Parse the hypothetical transaction files, and add them to a mapping of
    # filename to transaction list.
    # While doing that, also add to the `stock_tickers` set.
    hypothetical_transactions: typing.Dict[str, typing.List[tr.Transaction]] = {}
    for hyp_transaction_file in hypotheticals:
        file_path = pathlib.Path(hyp_transaction_file)
        hyp_transaction_data = tr.parse_transaction_file(file_path)
        hypothetical_transactions[file_path.stem] = hyp_transaction_data           
        stock_tickers |= tr.get_unique_tickers(hyp_transaction_data)

    # Fetch data for the needed stock tickers, optionally saving to `save_dir`
    stock_data = sd.fetch_all_data(
        stock_tickers,
        start_date,
        end_date,
        write_to_dir=pathlib.Path(save_dir),
    )

    # Calculate statistics for the main portfolio
    stock_stats = an.calc_per_stock_stats(
        transactions,
        stock_data,
        start_date,
        end_date,
    )
    # Print stats to console.
    print('Stock Stats')
    for ticker, stats in stock_stats.items():
        print('{}: {}'.format(ticker, stats))
    # Write to file
    # with open(pathlib.Path(save_dir) / 'stats.json', 'w') as out_file:
    #     json.dump(stock_stats, out_file, indent=4, default=str)

    # Calculate portfolio value for every day between `start_date` and
    # `end_date`, inclusive
    val_over_time = an.calc_value_over_time(
        starting_cash,
        transactions,
        stock_data,
        start_date,
        end_date,
    )
    # Write out value-over-time
    out_path = pathlib.Path(save_dir) / 'portfolio-vals.csv'
    with open(out_path, 'w') as vals_out:
        vals_out.write('Date,Value ($)\n')
        for date, value in val_over_time.items():
            vals_out.write('{},{}\n'.format(date, value))
    
    # Calculate valuations for each hypothetical portfolio
    hypothetical_vals_over_time: \
        typing.Dict[str, 'collections.OrderedDict[datetime.date, float]'] = {}
    for hyp_name, hyp_transactions in hypothetical_transactions.items():
        hypothetical_vals_over_time[hyp_name] = an.calc_value_over_time(
            starting_cash,
            hyp_transactions,
            stock_data,
            start_date,
            end_date,
        )

    # Draw and save plots
    fig, ax = plot.plot_portfolio(
        pathlib.Path(transaction_file).name,
        starting_cash,
        val_over_time,
        set(),
        hypothetical_vals_over_time,
    )
    fig.savefig(pathlib.Path(save_dir) / 'portfolio.jpg')


if __name__ == '__main__':
    run()
