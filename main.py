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
    date: datetime.datetime
    num_shares: int
    price_per_share: float


def parse_transaction_file(
        filepath: pathlib.Path,
) -> typing.List[Transaction]:
    transactions: typing.List[Transaction] = []
    with open(filepath, 'r') as transaction_file:
        line_num = 0
        for line in transaction_file:
            line_num += 1
            type_str, ticker, date_str, num_str, price_str = line.split()
            
            if type_str == 'BUY':
                t_type = TransactionType.BUY
            elif type_str == 'SELL':
                t_type = TransactionType.SELL
            else:
                raise ValueError(
                    'Invalid transaction type! (Line {}, col {})'.format(
                        line_num, 1)
                )

            date = datetime.datetime.strptime(date_str, r'%m/%d/%Y')
            num_shares = int(num_str)
            price = float(price_str)

            transactions.append(Transaction(
                t_type,
                ticker,
                date,
                num_shares,
                price,
            ))
    return transactions

            
transaction_file = 'transaction-history.txt'
transactions = parse_transaction_file(transaction_file)
print(transactions)