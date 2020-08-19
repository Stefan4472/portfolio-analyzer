import collections
import typing
# from matplotlib import pyplot as plt
import matplotlib


def plot_portfolio(
        title: str,
        starting_cash: float,
        val_over_time: 'collections.OrderedDict[datetime.date, float]',
        hypotheticals: typing.Set[str],
        hyp_val_over_time: typing.Dict[str, 'collections.OrderedDict[datetime.date, float]'],
) -> typing.Tuple['matplotlib.figure.Figure', 'matplotlib.axes._subplots.AxesSubplot']:
    # Note: I'm not sure how to properly type-hint the Pyplot `fig, ax` values
    fig, ax = matplotlib.pyplot.subplots()
    fig.suptitle('Portfolio Value Over Time')
    # Plot portfolio data
    ax.plot(
        val_over_time.keys(), 
        val_over_time.values(), 
        label=title,
    )
    # Plot hypothetical portfolios
    for hyp_name in hypotheticals:
        ax.plot(
            hyp_vals_over_time[hyp_name].keys(),
            hyp_vals_over_time[hyp_name].values(),
            label=hyp_name,
            linestyle='--',
        )
    # Plot dotted horizontal line with starting value
    ax.axhline(starting_cash, color='r', linestyle='--')
    # Apply further configuration
    ax.grid(True)
    fig.legend()

    return fig, ax