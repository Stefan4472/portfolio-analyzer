from pathlib import Path

from finance_cache.finance_cache import FinanceCache

if __name__ == "__main__":
    """Just a quick test script."""
    cache = FinanceCache(Path(r"C:\Users\Stefan\Github\portfolio-analyzer\cache"))
    print(cache.get_price_history('MSFT'))
