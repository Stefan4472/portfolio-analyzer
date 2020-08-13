import datetime
import typing
import click
from matplotlib import pyplot as plt
import transactions as tr
import stock_data as sd
import analyze as an

@click.command()
@click.argument('starting_cash', type=float)
@click.argument('transaction_file')
@click.option('-s', '--start_date', type=click.DateTime((r'%Y-%m-%d',)))
@click.option('-e', '--end_date', type=click.DateTime((r'%Y-%m-%d',)))
@click.option('-h', '--hypotheticals', type=click.Path(exists=True), multiple=True)
@click.option('-o', '--out_file', type=click.Path(exists=True))
# TODO: DOUBLE-CHECK TYPES
def run(
        starting_cash: float,
        transaction_file: str,
        start_date: datetime.datetime = None,
        end_date: datetime.datetime = None,
        hypotheticals: typing.Tuple[str] = None,
        out_file: str = None,
):
    """
    Note: ideally, we would make '-s' AND '-e' required, or neither. That is
    possible, but not really wor
    """
    print(hypotheticals)
    print(out_file)
    transactions = tr.parse_transaction_file(transaction_file)
    
    # Require either `start_date` AND `end_date` to be defined, or neither
    if (start_date and not end_date) or (end_date and not start_date):
        raise ValueError('start_date and end_date must be both defined, or neither defined')

    # Default `start_date`, `end_date` to the first/last transactions
    start_date = start_date.date() if start_date else transactions[0].date
    end_date = end_date.date() if end_date else transactions[-1].date
    if start_date > end_date:
        raise ValueError('start_date must come chronologically before end_date')
    # data = fetch_stock_data(
    #     'NFLX',
    #     datetime.date(year=2020, month=3, day=10),
    #     datetime.date(year=2020, month=5, day=2),
    #     write_to='nflx-data.csv',
    # )
    stock_data = {}
    with open('nflx-data.csv', 'r') as data_file:
        stock_data['NFLX'] = sd.read_stock_datafile(data_file)
    with open('aapl-data.csv', 'r') as data_file:
        stock_data['AAPL'] = sd.read_stock_datafile(data_file)
    print(an.calc_per_stock_stats(
        transactions,
        stock_data,
        start_date,
        end_date,
    ))
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
    plt.show()


if __name__ == '__main__':
    run()
