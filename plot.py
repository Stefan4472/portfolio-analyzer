import collections
import typing
import matplotlib.pyplot as plt


def create_portfolio_plot(
        starting_cash: float,
        vals_over_time: typing.Dict[str, 'collections.OrderedDict[datetime.date, float]'],
        portfolios_to_plot: typing.Set[str],
        title: str = 'Portfolio Value Over Time',
) -> typing.Tuple['matplotlib.figure.Figure', 'matplotlib.axes._subplots.AxesSubplot']:
    fig, ax = plt.subplots()
    print(vals_over_time)
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
    # Only plotting one portfolio: place legend in "best" position
    # (usually upper-right) 
    if len(portfolios_to_plot) == 1:
        fig.legend()
    else:
        # Plotting multiple portfolios: place legend at upper left,
        # inside plot (so as to avoid covering part of the graph).
        # Note: this was determined qualitatively based on what looked
        # best for the example portfolios.
        fig.legend(loc='upper left', bbox_to_anchor=(0.15, 0.85))

    return fig, ax