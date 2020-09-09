import json
import datetime
import typing
import transactions as tr


class Portfolio:
    def __init__(
        self,
        name: str,
        transactions: typing.List[tr.Transaction],
    ):
        self.name = name
        self.transactions = transactions

    @staticmethod
    def from_json(json_dict: typing.Dict[str, typing.Any]) -> 'Portfolio':
        if 'name' not in json_dict:
            raise ValueError('Missing "name" key')
        if not isinstance(json_dict['name'], str):
            raise ValueError('"name" value must be a string')
        if 'transactions' not in json_dict:
            raise ValueError('Missing "transactions" list')
        if not isinstance(json_dict['transactions'], list):
            raise ValueError('"transactions" value must be a list')

        name: str = json_dict['name']
        transactions: typing.List[Transaction] = []

        # TODO: ARE THESE PARSED IN-ORDER? CAN WE TELL THE USER THE INDEX OF THE TRANSACTION THAT FAILED?
        for transaction_json in json_dict['transactions']:
            print(transaction_json)
            # TODO: USE JSONSCHEMA
            if 'date' not in transaction_json:
                raise ValueError('Transaction missing "date" field')
            if not isinstance(transaction_json['date'], str):
                raise ValueError('"date" value must be a string')

            if 'ticker' not in transaction_json:
                raise ValueError('Transaction missing "ticker" field')
            if not isinstance(transaction_json['ticker'], str):
                raise ValueError('"ticker" value must be a string')

            if 'type' not in transaction_json:
                raise ValueError('Transaction missing "type" field')
            if not isinstance(transaction_json['type'], str):
                raise ValueError('"type" value must be a string')

            if 'volume' not in transaction_json:
                raise ValueError('Transaction missing "volume" field')
            if not isinstance(transaction_json['volume'], int):
                raise ValueError('"date" value must be an int')

            if 'price' not in transaction_json:
                raise ValueError('Transaction missing "price" field')
            if not isinstance(transaction_json['price'], float):
                raise ValueError('"date" value must be a float')

            if transaction_json['type'] == 'BUY':
                transaction_type = tr.TransactionType.BUY
            elif transaction_json['type'] == 'SELL':
                transaction_type = tr.TransactionType.SELL
            else:
                raise ValueError('Invalid type "{}"'.format(transaction_json['type']))
            
            # TODO: CHECK ERROR
            date = datetime.datetime.strptime(transaction_json['date'], r'%m/%d/%Y').date()

            transactions.append(tr.Transaction(
                transaction_type,
                transaction_json['ticker'],
                date,
                transaction_json['volume'],
                transaction_json['price'],
            ))
        # Sort by date, ascending
        transactions.sort(key=lambda t: t.date)
        return transactions


if __name__ == '__main__':
    with open('example/portfolio-1.json', 'r') as f:
        json_dict = json.load(f)
        Portfolio.from_json(json_dict)