import abc

import pandas as pd


class PersistenceDataFrameIO(abc.ABC):
    """
    Interface that is able to read tabular data from a persistent source as a dataframe, and then save it back.
    """
    @abc.abstractmethod
    def read_dataframe(self) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def save_dataframe(self, dataframe: pd.DataFrame):
        pass
