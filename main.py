import os
import datetime
import typing
import click
import pathlib
import json
import collections
from matplotlib import pyplot as plt
import portfolio as pf
import transactions as tr
import stock_data as sd
import analyze as an
import plot


@click.command()
@click.argument('starting_cash', type=float)
@click.argument('portfolio_files', type=click.Path(exists=True, readable=True), nargs=-1)
@click.option('-s', '--start_date', type=click.DateTime((r'%Y-%m-%d',)), required=True)
@click.option('-e', '--end_date', type=click.DateTime((r'%Y-%m-%d',)), required=True)
@click.option('--save_dir', type=click.Path(file_okay=False, dir_okay=True, writable=True), default=os.getcwd())
@click.option('--quiet', type=bool, default=False)
def run(
        starting_cash: float,
        portfolio_files: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        save_dir: str,
        quiet: bool,
):
    """Run the portfolio-analyzer program on the specified user-defined
    portfolio files.

    The user must provide the amount of starting cash that was used to 
    make all purchases (and is constant across all specified portfolios). 
    This amount should be big enough to afford the purchase of all holdings
    in each specified portfolio.

    The user must also provide an arbitrary number of portfolio JSON
    files, which will be analyzed and plotted. These files should 
    follow the format demonstrated in the example.

    Specify a save directory using the `--save_dir` option (recommended). 
    Otherwise, all created files and charts will be saved to the directory
    of execution.

    Specify start and end dates to analyze the portfolios over using the 
    `-s` and `-e` options, respectively.

    Author: Stefan Kussmaul (https://github.com/Stefan4472)
    """
    if end_date <= start_date:
        raise ValueError('end_date must come chronologically after start_date')

    # Create save directory if it doesn't already exist
    save_path = pathlib.Path(save_dir)
    save_path.mkdir(exist_ok=True)

    # Create directory for stock data
    data_path = save_path / 'stock-data'
    data_path.mkdir(exist_ok=True)

    # Create cache for stock data
    stock_data_cache = sd.StockDataCache(
        start_date, 
        end_date,
        write_to_dir=data_path,
        quiet=quiet,
    ) 

    # Map portfolio name to Portfolio instance  TODO: ACTUALLY ISN'T USED
    all_portfolios: typing.Dict[str, pf.Portfolio] = {}
    # Map portfolio name to StockPriceHistory
    all_history: typing.Dict[str, sd.StockPriceHistory] = {}

    # Parse and analyze each portfolio file
    for portfolio_path in portfolio_files:
        with open(portfolio_path, 'r') as portfolio_file:
            portfolio = pf.Portfolio.from_json(json.load(portfolio_file))
        all_portfolios[portfolio.name] = portfolio

        # Create save dir
        portfolio_path = save_path / portfolio.name
        portfolio_path.mkdir(exist_ok=True)

        # Calculate statistics for each stock holding in the portfolio
        per_stock_stats = portfolio.calc_statistics(
            starting_cash,
            start_date.date(),
            end_date.date(),
            stock_data_cache,
        )

        # Write stats to file
        with open(portfolio_path / 'stats.json', 'w') as out_file:
            # Sort items ascending by annualized return
            sorted_stats = sorted(
                per_stock_stats.items(), 
                key=lambda s: s[1].annualized_return, 
                reverse=True,
            )
            # Construct OrderedDict mapping ticker -> {stats-JSON}.
            # This is necessary to dump the statistics in sorted order.
            stats_json = collections.OrderedDict()
            for ticker, stats in sorted_stats:
                stats_json[ticker] = stats.to_json()
            # Write out, calling `str()` on each item
            json.dump(stats_json, out_file, indent=4, default=str)

        # Calculate portfolio value for every day between `start_date` and
        # `end_date`, inclusive
        val_over_time = portfolio.calc_value_over_time(
            starting_cash,
            start_date.date(),
            end_date.date(),
            stock_data_cache,
        )

        # Write out value-over-time
        out_path = portfolio_path / (portfolio.name + '.csv')
        with open(out_path, 'w') as vals_out:
            vals_out.write('Date,Value at Close ($)\n')
            for date, value in val_over_time.items():
                vals_out.write('{},{}\n'.format(date, value))

        # Add to mapping
        all_history[portfolio.name] = val_over_time

        # Draw and save plot
        fig, ax = plot.create_portfolio_plot(
            starting_cash,
            all_history,
            set([portfolio.name,]),
        )
        fig.savefig(
            portfolio_path / (portfolio.name + '.jpg'), 
            bbox_inches='tight',
        )

    # TODO: BEST PRACTICE FOR PRINTING TO CONSOLE?
    if not quiet:
        print('Plotting comparisons...')

    # Create one plot with all portfolios
    fig, ax = plot.create_portfolio_plot(
        starting_cash,
        all_history,
        all_history.keys()
    )
    fig.savefig(
        save_path / 'portfolio-comparison.jpg', 
        bbox_inches='tight',
    )

    if not quiet:
        print('Done')


if __name__ == '__main__':
    run()
