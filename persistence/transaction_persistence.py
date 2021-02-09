from dataclasses import dataclass
from typing import Dict, Sequence, Callable
import io
import datetime as dt

import pandas as pd

from security import Security
from persistence import PersistenceTextIO

SECURITY_ID = 'security_id'
TRANSACTION_SHARE_AMOUNT = 'transaction_share_amount'
TRANSACTION_DATE = 'transaction_date'


@dataclass
class ShareTransaction:
    security_id: str
    transaction_share_amount: int
    transaction_date: dt.datetime


class TransactionPersistence:
    def __init__(self, text_reader: PersistenceTextIO):
        self._text_io = text_reader
        self._transactions_csv = self._text_io.read_text()

    def read_portfolio(self) -> Dict[Security, int]:
        """
        Reads the amount of shares that are in the portfolio from the file
        that records all the transactions.
        :return: The portfolio in amount of shares
        """
        transactions_buffer = io.StringIO(self._transactions_csv)
        transactions_df = pd.read_csv(transactions_buffer, sep=';')[[SECURITY_ID, TRANSACTION_SHARE_AMOUNT]]
        aggregated_portfolio = transactions_df.groupby(SECURITY_ID).sum()

        security_to_amount = aggregated_portfolio[TRANSACTION_SHARE_AMOUNT].to_dict()
        return {Security(sec_id): amount for sec_id, amount in security_to_amount.items()}

    def save_transactions(self, new_transactions: Sequence[ShareTransaction]):
        """
        Appends new transactions to the file that persists the transactions.
        :param new_transactions: Transactions to save.
        """
        transactions_buffer = io.StringIO(self._transactions_csv)
        transactions_df = pd.read_csv(transactions_buffer, sep=';')
        new_transactions = pd.DataFrame(new_transactions)
        combined_df = transactions_df.append(new_transactions)

        result_buffer = io.StringIO('')
        combined_df.to_csv(result_buffer, sep=';', index=False)

        self._transactions_csv = result_buffer.getvalue()
        self._text_io.save_text(self._transactions_csv)

    def read_portfolio_history(self, price_provider: Callable[[Security, dt.datetime], float]) -> Dict[dt.datetime, float]:
        """
        Reads the history of the portfolio
        :return: A dictionary whose key is a date, and whose value is the value of the portfolio at that time
        """
        transactions_buffer = io.StringIO(self._transactions_csv)
        transactions_df = pd.read_csv(transactions_buffer, sep=';')
        transactions_df[TRANSACTION_DATE] = pd.to_datetime(transactions_df[TRANSACTION_DATE])

        dated_transactions = transactions_df.set_index(TRANSACTION_DATE).sort_index()
        all_share_ids = dated_transactions[SECURITY_ID].unique()

        history_series = pd.Series(0, index=dated_transactions.index.unique())
        for share_id in all_share_ids:
            relevant_rows = dated_transactions[SECURITY_ID] == share_id
            cumulative_shares = dated_transactions.loc[relevant_rows, TRANSACTION_SHARE_AMOUNT].cumsum()

            def transform_row(row: pd.Series):
                transaction_date = row[TRANSACTION_DATE]
                share_amount = row[TRANSACTION_SHARE_AMOUNT]
                price = share_amount * price_provider(Security(share_id), transaction_date.to_pydatetime())
                return pd.Series([transaction_date, price], index=[TRANSACTION_DATE, 'Price'])

            prices = cumulative_shares.reset_index().apply(transform_row).groupby(TRANSACTION_DATE).sum()

            relevant_dates = history_series.index == prices.index
            history_series[relevant_dates] = history_series[relevant_dates] + prices.values

        return {date.to_pydatetime(): price for date, price in history_series.to_dict().items()}
