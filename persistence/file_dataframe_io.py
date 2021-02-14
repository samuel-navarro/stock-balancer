import pandas as pd

from persistence import PersistenceDataFrameIO


class FileDataFrameIO(PersistenceDataFrameIO):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def read_dataframe(self) -> pd.DataFrame:
        return pd.read_csv(self._file_name, sep=';')

    def save_dataframe(self, dataframe: pd.DataFrame):
        dataframe.to_csv(self._file_name, sep=';')
