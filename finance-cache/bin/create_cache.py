from datetime import date
from pathlib import Path

import click
from finance_cache.config import CacheConfig
from finance_cache.finance_cache import FinanceCache


@click.command()
@click.argument("cache_path", type=click.Path(path_type=Path, exists=False))
@click.option(
    "--history_start",
    required=True,
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="The start date of price history that the cache will load. It will not"
         " attempt to load or store data older than this date.",
)
def create_cache(cache_path: Path, history_start: date):
    """
    Creates an instance of the finance cache with the specified options.

    CACHE_PATH: The directory where the data loaded by the cache will live.
      This directory will be created and must not already exist.
    """
    FinanceCache.create(cache_path, CacheConfig(history_start))
    click.echo("Success.")


if __name__ == "__main__":
    create_cache()
