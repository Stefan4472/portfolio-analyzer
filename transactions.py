import datetime
import enum
import typing
import pathlib
import dataclasses as dc


class TransactionType(enum.Enum):
    BUY = 1
    SELL = 2


@dc.dataclass
class Transaction:
    type: TransactionType
    ticker: str
    date: datetime.date
    volume: int
    price_per_share: float


def parse_transaction_file(
        filepath: pathlib.Path,
) -> typing.List[Transaction]:
    transactions: typing.List[Transaction] = []
    with open(filepath, 'r') as transaction_file:
        line_num = 0
        for line in transaction_file:
            line_num += 1
            type_str, ticker, date_str, volume_str, price_str = line.split()
            
            if type_str == 'BUY':
                t_type = TransactionType.BUY
            elif type_str == 'SELL':
                t_type = TransactionType.SELL
            else:
                raise ValueError(
                    'Invalid transaction type! (Line {}, col {})'.format(
                        line_num, 1)
                )

            date = datetime.datetime.strptime(date_str, r'%m/%d/%Y').date()
            volume = int(volume_str)
            price = float(price_str)

            transactions.append(Transaction(
                t_type,
                ticker,
                date,
                volume,
                price,
            ))
    # Sort by date, ascending
    transactions.sort(key=lambda t: t.date)
    return transactions


def get_unique_tickers(
        transactions: typing.List[Transaction],
) -> typing.Set[str]:
    return set(t.ticker for t in transactions)