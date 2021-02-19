import unittest
from datetime import datetime

import pandas as pd

from persistence import transaction_persistence as tr
from persistence import PersistenceDataFrameIO
from data_types import Security

TRANSACTIONS = [
    tr.ShareTransaction(security_id='AAPL', transaction_share_amount=10, transaction_date=datetime(2020, 1, 1)),
    tr.ShareTransaction(security_id='TSLA', transaction_share_amount=10, transaction_date=datetime(2020, 1, 1)),
    tr.ShareTransaction(security_id='AMZN', transaction_share_amount=10, transaction_date=datetime(2020, 1, 1)),
    tr.ShareTransaction(security_id='AAPL', transaction_share_amount=-5, transaction_date=datetime(2020, 1, 4)),
    tr.ShareTransaction(security_id='TSLA', transaction_share_amount=5, transaction_date=datetime(2020, 1, 5)),
]


class TestDataFrameIO(PersistenceDataFrameIO):
    def __init__(self):
        self.saved_dataframes = []

    def read_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(TRANSACTIONS)

    def save_dataframe(self, dataframe: pd.DataFrame):
        self.saved_dataframes.append(dataframe)


class EmptyDataFrameIO(PersistenceDataFrameIO):
    def read_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame()

    def save_dataframe(self, dataframe: pd.DataFrame):
        pass


class TransactionPersistenceTests(unittest.TestCase):
    def test_read_portfolio(self):
        test_io = TestDataFrameIO()
        persistence = tr.TransactionPersistence(test_io)
        portfolio = persistence.read_portfolio()

        self.assertEqual(portfolio[Security('AAPL')], 5)
        self.assertEqual(portfolio[Security('TSLA')], 15)
        self.assertEqual(portfolio[Security('AMZN')], 10)

    def test_save_transactions(self):
        test_io = TestDataFrameIO()
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

    def test_read_history(self):
        dated_prices = {
            datetime(2020, 1, 1): {
                Security('AAPL'): 10,
                Security('AMZN'): 20,
                Security('TSLA'): 30
            },

            datetime(2020, 1, 4): {
                Security('AAPL'): 50,
                Security('AMZN'): 20,
                Security('TSLA'): 30
            },

            datetime(2020, 1, 5): {
                Security('AAPL'): 1,
                Security('AMZN'): 2,
                Security('TSLA'): 3
            }
        }

        def get_price(sec: Security, date: datetime) -> float:
            return dated_prices.get(date, dict()).get(sec)

        test_io = TestDataFrameIO()
        persistence = tr.TransactionPersistence(test_io)

        portfolio_history = persistence.read_portfolio_history(get_price)
        expected_history = {
            datetime(2020, 1, 1): 100+200+300,
            datetime(2020, 1, 4): 250+200+300,
            datetime(2020, 1, 5): 5+20+45
        }

        for date, price in portfolio_history.items():
            self.assertAlmostEqual(price, expected_history.get(date, -1))

    def test_read_empty_portfolio(self):
        test_io = EmptyDataFrameIO()
        persistence = tr.TransactionPersistence(test_io)
        portfolio = persistence.read_portfolio()

        self.assertEqual(len(portfolio.keys()), 0)

    def test_read_empty_history(self):
        test_io = EmptyDataFrameIO()
        persistence = tr.TransactionPersistence(test_io)
        history = persistence.read_portfolio_history(lambda sec, date: 0.0)

        self.assertEqual(len(history.keys()), 0)
