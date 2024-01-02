import json
from datetime import datetime
from pathlib import Path

import click
from finance_cache.finance_cache import FinanceCache
from marshmallow import Schema, fields


class TickersFileSchema(Schema):
    tickers = fields.List(fields.Str())


@click.command()
@click.argument(
    "cache_path", type=click.Path(file_okay=False, dir_okay=True, path_type=Path)
)
@click.argument(
    "tickers_file",
    type=click.Path(
        file_okay=True, dir_okay=False, exists=True, readable=True, path_type=Path
    ),
)
def preload_cache(cache_path: Path, tickers_file: Path):
    """
    Sends the FinanceCache requests to update data for all the tickers in `tickers_file`.
    """
    with open(tickers_file) as f:
        input_json = json.load(f)
        tickers = TickersFileSchema().load(input_json)["tickers"]

    click.echo(f"Received {len(tickers)} tickers to load.")
    start_time = datetime.now()
    cache = FinanceCache(cache_path)
    for ticker in tickers:
        # TODO: catch exception, e.g. ticker not found
        cache.load(ticker)
    click.echo(f"Finished in {(datetime.now() - start_time).seconds} seconds.")


if __name__ == "__main__":
    preload_cache()
