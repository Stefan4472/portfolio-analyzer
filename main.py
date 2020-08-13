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
def run(
        starting_cash: float,
        transaction_file: str,
):
    transactions = tr.parse_transaction_file(transaction_file)
    
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
        datetime.date(year=2020, month=3, day=10),
        datetime.date(year=2020, month=5, day=1),
    ))
    val_over_time = an.calc_value_over_time(
        starting_cash,
        transactions,
        stock_data,
        datetime.date(year=2020, month=3, day=10),
        datetime.date(year=2020, month=5, day=1),
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
