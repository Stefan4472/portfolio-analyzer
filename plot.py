import collections
import typing
# from matplotlib import pyplot as plt
import matplotlib


# TODO: THE TYPING FOR `VALS_OVER_TIME` IS ACTUALLY INCORRECT
def create_portfolio_plot(
        starting_cash: float,
        vals_over_time: 'collections.OrderedDict[datetime.date, float]',
        portfolios_to_plot: typing.Set[str],
        title: str = 'Portfolio Value Over Time',
) -> typing.Tuple['matplotlib.figure.Figure', 'matplotlib.axes._subplots.AxesSubplot']:
    # Note: I'm not sure how to properly type-hint the Pyplot `fig, ax` values
    fig, ax = matplotlib.pyplot.subplots()
    fig.suptitle(title)
    ax.set_xlabel('Date')
    ax.set_ylabel('Value at Close ($)')
    # Plot portfolio data
    for portfolio_name in portfolios_to_plot:
        ax.plot(
            vals_over_time[portfolio_name].keys(),
            vals_over_time[portfolio_name].values(),
            label=portfolio_name,
            linestyle='--',
        )
    # Plot dotted horizontal line with starting value
    ax.axhline(starting_cash, color='r', linestyle='--')
    ax.grid(True)
    # Rotate x-axis ticks to avoid cramping
    ax.tick_params(axis='x', labelrotation=20)
    # Place legend to the upper right, outside the plot:
    # https://stackoverflow.com/a/43832425
    # if len(portfolios_to_plot) == 1:
    #     fig.legend()
    # else:
    #     fig.legend(loc=(0.8, 0.7))
    fig.legend()
    return fig, ax