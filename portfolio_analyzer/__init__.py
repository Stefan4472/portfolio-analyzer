import datetime
from datetime import datetime
from pathlib import Path

import flask
from finance_cache.finance_cache import FinanceCache
from flask import Flask


def create_app():
    """Creates the Flask app. Uses the provided `test_config`, if non-Null."""
    app = Flask(__name__, instance_relative_config=True)
    instance = Path(app.instance_path)
    instance.mkdir(exist_ok=True)
    app.config["FINANCE_CACHE"] = FinanceCache(
        Path(app.instance_path) / "finance_cache", datetime(year=2015, month=1, day=1)
    )

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route("/<string:ticker>")
    def get_ticker(ticker: str):
        # TODO: implement a better mechanism to pre-load the cache.
        history = app.config["FINANCE_CACHE"].get_price_history(ticker)
        as_json = {str(h.day): h.close for h in history}
        return flask.make_response(as_json)

    return app
