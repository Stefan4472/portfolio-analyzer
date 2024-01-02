from dataclasses import dataclass
from datetime import date

from marshmallow import Schema, fields, post_load


@dataclass(frozen=True)
class CacheConfig:
    """Configuration for FinanceCache instances."""

    # The start date of price history that the cache will load. It will not
    # attempt to load or store data older than this date.
    history_start: date


class CacheConfigSchema(Schema):
    """Marshmallow schema used to validate a `CacheConfig` instance."""

    history_start = fields.Date(required=True)

    @post_load
    def make_config(self, data, **kwargs) -> CacheConfig:
        return CacheConfig(**data)
