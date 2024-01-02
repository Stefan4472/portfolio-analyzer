from dataclasses import dataclass
from os import environ

from dotenv import load_dotenv
from marshmallow import Schema, fields, post_load


@dataclass(frozen=True)
class AppConfig:
    """Configuration for a portfolio-analyzer app instance."""

    # Base path to the FinanceCache instance to use.
    cache_path: str

    @staticmethod
    def from_environment() -> "AppConfig":
        """Loads the config from environment variables."""
        # Attempt to load a `.flaskenv` configuration file.
        load_dotenv(".flaskenv")
        config = AppConfig(
            environ.get("PORTFOLIO_ANALYZER_CACHE_PATH"),
        )

        errors = AppConfigSchema().validate(AppConfigSchema().dump(config))
        if errors:
            raise ValueError(
                f"Failed to load app configuration from environment variables "
                f"due to the following issues: {errors}"
            )

        return config


class AppConfigSchema(Schema):
    """Marshmallow schema used to validate a `CacheConfig` instance."""

    cache_path = fields.String(required=True, data_key="PORTFOLIO_ANALYZER_CACHE_PATH")

    @post_load
    def make_config(self, data, **kwargs) -> AppConfig:
        return AppConfig(**data)
