import datetime
import json
from datetime import datetime
from pathlib import Path

from finance_cache.finance_cache import FinanceCache
from flask import Flask, Response, make_response, request

from portfolio_analyzer.analyze import (calculate_value_over_time,
                                        preprocess_portfolio)
from portfolio_analyzer.portfolio import PortfolioSchema


def create_app():
    """Creates the Flask app. Uses the provided `test_config`, if non-Null."""
    app = Flask(__name__, instance_relative_config=True)
    instance = Path(app.instance_path)
    instance.mkdir(exist_ok=True)
    app.config["FINANCE_CACHE"] = FinanceCache(
        Path(app.instance_path) / "finance_cache", datetime(year=2015, month=1, day=1)
    )

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    @app.route("/ticker/<string:ticker>")
    def get_ticker(ticker: str):
        # TODO: implement a better mechanism to pre-load the cache.
        history = app.config["FINANCE_CACHE"].get_price_history(
            ticker,
            datetime(year=2022, month=1, day=1).date(),
            datetime(year=2023, month=1, day=1).date(),
        )
        as_json = [{"date": str(h.day), "value": h.close} for h in history.values()]
        response = make_response(as_json)
        # TODO: remove. Just using this as a quick workaround for now.
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    # TODO: allow specifying start and end date.
    @app.route("/portfolio", methods=["POST"])
    def process_portfolio():
        try:
            as_json = json.loads(request.data.decode("ascii"))
            raw_portfolio = PortfolioSchema().load(as_json)
            processed_portfolio = preprocess_portfolio(raw_portfolio)
            print(processed_portfolio)
            res = calculate_value_over_time(
                processed_portfolio,
                10000,
                datetime(year=2020, month=3, day=1).date(),
                datetime(year=2020, month=4, day=1).date(),
                app.config["FINANCE_CACHE"],
            )
            as_json = {str(r.date): r.value for r in res}
            print(as_json)
            return make_response(as_json)
        except Exception as e:
            print(e)
            return Response(status=500)

    return app
