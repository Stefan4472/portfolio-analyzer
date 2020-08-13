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
    # Require either `start_date` AND `end_date` to be defined, or neither
    if (start_date and not end_date) or (end_date and not start_date):
        raise ValueError('start_date and end_date must be both defined, or neither defined')

    # Parse transactions file
    transactions = tr.parse_transaction_file(pathlib.Path(transaction_file))

    # Default `start_date`, `end_date` to the first/last transactions
    start_date = start_date.date() if start_date else transactions[0].date
    end_date = end_date.date() if end_date else transactions[-1].date
    if start_date > end_date:
        raise ValueError('start_date must come chronologically before end_date')

    # Create save directory if it doesn't already exist
    if save_dir:
        pathlib.Path(save_dir).mkdir(exist_ok=True)

    # Set of all stock tickers required
    stock_tickers: typing.Set[str] = tr.get_unique_tickers(transactions)

    # Map filenames of hypothetical transactions to lists of those transactions.
    # While doing that, also add to the `stock_tickers` set.
    hyp_transactions: typing.Dict[str, typing.List[tr.Transaction]] = {}
    for hyp_transaction_file in hypotheticals:
        file_path = pathlib.Path(hyp_transaction_file)
        hyp_transactions[file_path.stem] = tr.parse_transaction_file(file_path)
        stock_tickers |= tr.get_unique_tickers(hyp_transactions[file_path.stem])

    # Fetch data for the needed stock tickers
    stock_data = sd.fetch_all_data(
        stock_tickers,
        start_date,
        end_date,
        write_to_dir=pathlib.Path(save_dir) if save_dir else None,
    )

    # Calculate statistics for the main portfolio and optionally write to file
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
    # TODO: WRITE OUT PORTFOLIO VALUE-OVER-TIME TO FILE
    
    # Calculate valuations for hypothetical portfolios
    hypothetical_vals: \
        typing.Dict[str, 'collections.OrderedDict[datetime.date, float]'] = {}
    for hyp_name, _hyp_transactions in hyp_transactions.items():
        hypothetical_vals[hyp_name] = an.calc_value_over_time(
            starting_cash,
            _hyp_transactions,
            stock_data,
            start_date,
            end_date,
        )

    # Plotting
    fig, ax = plt.subplots()
    fig.suptitle('Portfolio Value Over Time')
    ax.plot(
        val_over_time.keys(), 
        val_over_time.values(), 
        label=pathlib.Path(transaction_file).name,
    )
    # Plot hypothetical portfolios
    for hyp_name, hyp_vals_over_time in hypothetical_vals.items():
        fig2, ax2 = plt.subplots()
        fig2.suptitle('Portfolio Value Over Time')
        ax2.plot(hyp_vals_over_time.keys(), hyp_vals_over_time.values())
        ax2.axhline(starting_cash, color='r', linestyle='--')
        ax2.grid(True)
        fig.savefig(pathlib.Path(save_dir) / (hyp_name + '.jpg'))

        # Add to main plot
        ax.plot(
            hyp_vals_over_time.keys(),
            hyp_vals_over_time.values(),
            label=hyp_name,
            linestyle='--',
        )

    # Plot dotted horizontal line with starting value
    ax.axhline(starting_cash, color='r', linestyle='--')
    ax.grid(True)
    fig.legend()
    if show_plots:
        fig.show()
    if save_dir:
        fig.savefig(pathlib.Path(save_dir) / 'portfolio.jpg')


if __name__ == '__main__':
    run()
