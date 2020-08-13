import datetime
import typing
import click
import pathlib
import json
from matplotlib import pyplot as plt
import transactions as tr
import stock_data as sd
import analyze as an

@click.command()
@click.argument('starting_cash', type=float)
@click.argument('transaction_file')
@click.option('--start_date', type=click.DateTime((r'%Y-%m-%d',)))
@click.option('--end_date', type=click.DateTime((r'%Y-%m-%d',)))
@click.option('-h', '--hypotheticals', type=click.Path(exists=True), multiple=True)
@click.option('-s', '--save_dir', type=click.Path())
@click.option('--show_plots', type=bool, default=True)
# TODO: DOUBLE-CHECK TYPES
def run(
        starting_cash: float,
        transaction_file: str,
        start_date: datetime.datetime = None,
        end_date: datetime.datetime = None,
        hypotheticals: typing.Tuple[str] = None,
        save_dir: str = None,
        show_plots: bool = True,
):
    """
    Note: ideally, we would make '-s' AND '-e' required, or neither. That is
    possible, but not really wor
    """
    print(hypotheticals)
    print(show_plots)
    transactions = tr.parse_transaction_file(transaction_file)
    
    # Require either `start_date` AND `end_date` to be defined, or neither
    if (start_date and not end_date) or (end_date and not start_date):
        raise ValueError('start_date and end_date must be both defined, or neither defined')

    # Default `start_date`, `end_date` to the first/last transactions
    start_date = start_date.date() if start_date else transactions[0].date
    end_date = end_date.date() if end_date else transactions[-1].date
    if start_date > end_date:
        raise ValueError('start_date must come chronologically before end_date')

    # Create save directory if it doesn't already exist
    if save_dir:
        pathlib.Path(save_dir).mkdir(exist_ok=True)

    stock_data = sd.fetch_all_data(
        tr.get_unique_tickers(transactions),
        start_date,
        end_date,
        write_to_dir=pathlib.Path(save_dir) if save_dir else None,
    )

    # with open('nflx-data.csv', 'r') as data_file:
    #     stock_data['NFLX'] = sd.read_stock_datafile(data_file)
    # with open('aapl-data.csv', 'r') as data_file:
    #     stock_data['AAPL'] = sd.read_stock_datafile(data_file)

    stock_stats = an.calc_per_stock_stats(
        transactions,
        stock_data,
        start_date,
        end_date,
    )

    # Print stats to console.
    # The `default=str` argument tells `json` to call the `str()` function
    # on objects that it doesn't know how to serialize (e.g. `date` objects)
    print('Stock Stats')
    for ticker, stats in stock_stats.items():
        print('{}: {}'.format(ticker, stats))
    # print(json.dumps({ticker: vars(stats) for ticker, stats in stock_stats.items()}, indent=4, default=str))
    # if save_dir:
    # with open(pathlib.Path(save_dir) / 'stats.json', 'w') as out_file:
    #     json.dump(stock_stats, out_file, indent=4, default=str)

    val_over_time = an.calc_value_over_time(
        starting_cash,
        transactions,
        stock_data,
        start_date,
        end_date,
    )
    
    # Plotting
    fig, ax = plt.subplots()
    fig.suptitle('Portfolio Value Over Time')
    ax.plot(val_over_time.keys(), val_over_time.values())
    ax.axhline(starting_cash, color='r', linestyle='--')
    ax.grid(True)
    if show_plots:
        fig.show()
    if save_dir:
        fig.savefig(pathlib.Path(save_dir) / 'portfolio.jpg')


if __name__ == '__main__':
    run()
