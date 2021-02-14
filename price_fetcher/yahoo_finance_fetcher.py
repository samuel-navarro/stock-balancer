from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from data_types import Security


def get_price(security: Security, date: datetime) -> float:
    """
    Fetches the price of a given security on a given date using the Yahoo Finance API. The accuracy of this function
    is at the day level, and returns the average between the highs and lows of the day.
    """
    symbol = yf.Ticker(security.identifier)

    # Note: There is no data on weekends, so we have to look for data all the way until friday. The reason why
    # 3 is subtracted is that if the input date is today and today is monday, and the monday has not closed
    # the market yet, there is no data available and we'd need to go to the previous friday to get data.
    #
    # Also, end date is not included in the result data for some reason, which is why 1 day is added.
    start_date = date - timedelta(days=3)
    end_date = date + timedelta(days=1)

    dataframe = symbol.history(interval='1h', start=start_date, end=end_date)
    if dataframe.empty:
        dataframe = symbol.history(interval='1d', start=start_date, end=end_date)

    if dataframe.empty:
        raise Exception(f'Cannot find price data for security {security.identifier} at the date {date}')

    df_unique_dates = dataframe.groupby(dataframe.index).median()

    pandas_date = pd.to_datetime(date)
    closest_date = min(df_unique_dates.index, key=lambda d: abs(d - pandas_date))

    data_at_date = df_unique_dates.loc[closest_date]

    return (data_at_date['High'] + data_at_date['Low']) / 2.0


