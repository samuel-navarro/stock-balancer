from dataclasses import dataclass
from typing import Dict, Sequence, Callable
import io
import datetime as dt

import pandas as pd
import numpy as np

from security import Security
from persistence import PersistenceDataFrameIO

SECURITY_ID = 'security_id'
TRANSACTION_SHARE_AMOUNT = 'transaction_share_amount'
TRANSACTION_DATE = 'transaction_date'


@dataclass
class ShareTransaction:
    security_id: str
    transaction_share_amount: int
    transaction_date: dt.datetime


class TransactionPersistence:
    def __init__(self, dataframe_io: PersistenceDataFrameIO):
        self._dataframe_io = dataframe_io

        self._transactions_dataframe = self._dataframe_io.read_dataframe()
        self._transactions_dataframe[TRANSACTION_DATE] = pd.to_datetime(self._transactions_dataframe[TRANSACTION_DATE])

    def read_portfolio(self) -> Dict[Security, int]:
        """
        Reads the amount of shares that are in the portfolio from the file
        that records all the transactions.
        :return: The portfolio in amount of shares
        """
        transactions_df = self._transactions_dataframe[[SECURITY_ID, TRANSACTION_SHARE_AMOUNT]]
        aggregated_portfolio = transactions_df.groupby(SECURITY_ID).sum()

        security_to_amount = aggregated_portfolio[TRANSACTION_SHARE_AMOUNT].to_dict()
        return {Security(sec_id): amount for sec_id, amount in security_to_amount.items()}

    def save_transactions(self, new_transactions: Sequence[ShareTransaction]):
        """
        Appends new transactions to the file that persists the transactions.
        :param new_transactions: Transactions to save.
        """
        new_transactions = pd.DataFrame(new_transactions)
        self._transactions_dataframe = self._transactions_dataframe.append(new_transactions)

        self._dataframe_io.save_dataframe(self._transactions_dataframe)

    def read_portfolio_history(self, price_provider: Callable[[Security, dt.datetime], float]) -> Dict[dt.datetime, float]:
        """
        Reads the history of the portfolio
        :return: A dictionary whose key is a date, and whose value is the value of the portfolio at that time
        """
        dated_transactions = self._transactions_dataframe.set_index(TRANSACTION_DATE).sort_index()
        all_share_ids = dated_transactions[SECURITY_ID].unique()

        date_index = dated_transactions.index.unique()
        share_history = pd.DataFrame(0, index=date_index, columns=all_share_ids)
        for share_id in all_share_ids:
            relevant_rows = dated_transactions[SECURITY_ID] == share_id
            transactions = dated_transactions.loc[relevant_rows, TRANSACTION_SHARE_AMOUNT]
            share_history.loc[dated_transactions.index[relevant_rows], share_id] = transactions
            share_history[share_id] = share_history[share_id].cumsum()

        share_prices = pd.DataFrame(0, index=date_index, columns=all_share_ids)
        for share_id in all_share_ids:
            date_to_price = lambda date: price_provider(Security(share_id), date)
            share_prices[share_id] = np.vectorize(date_to_price)(date_index)

        portfolio = (share_prices * share_history).apply(np.sum, axis=1)

        return {date.to_pydatetime(): price for date, price in portfolio.to_dict().items()}
