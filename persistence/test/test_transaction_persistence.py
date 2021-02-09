import io
import unittest
from datetime import datetime

import pandas as pd

from persistence import transaction_persistence as tr
from persistence import PersistenceTextIO
from security import Security

TRANSACTIONS = [
    tr.ShareTransaction(security_id='AAPL', transaction_share_amount=10, transaction_date=datetime(2020, 1, 1)),
    tr.ShareTransaction(security_id='TSLA', transaction_share_amount=10, transaction_date=datetime(2020, 1, 1)),
    tr.ShareTransaction(security_id='AMZN', transaction_share_amount=10, transaction_date=datetime(2020, 1, 1)),
    tr.ShareTransaction(security_id='AAPL', transaction_share_amount=-5, transaction_date=datetime(2020, 1, 4)),
    tr.ShareTransaction(security_id='TSLA', transaction_share_amount=5, transaction_date=datetime(2020, 1, 5)),
]


class TestTextIO(PersistenceTextIO):
    def __init__(self):
        self.saved_dataframes = []

    def read_text(self):
        buffer = io.StringIO()
        dataframe = pd.DataFrame(TRANSACTIONS)

        dataframe.to_csv(buffer, sep=';', index=False)
        return buffer.getvalue()

    def save_text(self, text: str):
        buffer = io.StringIO(text)
        dataframe = pd.read_csv(buffer, sep=';')

        self.saved_dataframes.append(dataframe)


class TransactionPersistenceTests(unittest.TestCase):
    def test_read_portfolio(self):
        test_io = TestTextIO()
        persistence = tr.TransactionPersistence(test_io)
        portfolio = persistence.read_portfolio()

        self.assertEqual(portfolio[Security('AAPL')], 5)
        self.assertEqual(portfolio[Security('TSLA')], 15)
        self.assertEqual(portfolio[Security('AMZN')], 10)

    def test_save_transactions(self):
        test_io = TestTextIO()
        persistence = tr.TransactionPersistence(test_io)

        transactions_to_save = [
            tr.ShareTransaction('SPY', 5, datetime(2020, 2, 1)),
            tr.ShareTransaction('GE', 5, datetime(2020, 2, 2))
        ]

        persistence.save_transactions(transactions_to_save)
        all_transactions = TRANSACTIONS + transactions_to_save

        saved_transactions = test_io.saved_dataframes[-1]
        saved_transactions[tr.TRANSACTION_DATE] = pd.to_datetime(saved_transactions[tr.TRANSACTION_DATE])
        for index, expected_transaction in enumerate(all_transactions):
            saved_transaction = saved_transactions.iloc[index]
            self.assertEqual(saved_transaction[tr.SECURITY_ID], expected_transaction.security_id)
            self.assertEqual(saved_transaction[tr.TRANSACTION_SHARE_AMOUNT], expected_transaction.transaction_share_amount)
            self.assertEqual(saved_transaction[tr.TRANSACTION_DATE], expected_transaction.transaction_date)

