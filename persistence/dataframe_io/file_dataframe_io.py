from pathlib import Path

import pandas as pd

from persistence import PersistenceDataFrameIO


class FileDataFrameIO(PersistenceDataFrameIO):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def read_dataframe(self) -> pd.DataFrame:
        file_path = Path(self._file_name)

        if file_path.is_file():
            return pd.read_csv(self._file_name, sep='\t')
        else:
            return pd.DataFrame()

    def save_dataframe(self, dataframe: pd.DataFrame):
        dataframe.to_csv(self._file_name, sep='\t')
