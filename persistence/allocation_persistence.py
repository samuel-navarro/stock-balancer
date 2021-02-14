from typing import Dict

import pandas as pd

from persistence import PersistenceDataFrameIO
from data_types import Security


SECURITY_ID = "security_id"
ALLOCATION = "allocation_percentage"


class AllocationPercentagesPersistence:
    def __init__(self, dataframe_io: PersistenceDataFrameIO):
        self._dataframe_io = dataframe_io
        self._allocations = self._dataframe_io.read_dataframe()

    def read_allocation_percentages(self) -> Dict[Security, float]:
        ids_to_allocations = self._allocations.set_index(SECURITY_ID)[ALLOCATION].to_dict()
        return {Security(sec): value for sec, value in ids_to_allocations.items()}

    def write_allocation_percentages(self, allocations: Dict[Security, float]):
        dataframe = pd.Series({sec.identifier: value for sec, value in allocations.items()}).reset_index()
        dataframe.columns = [SECURITY_ID, ALLOCATION]

        self._dataframe_io.save_dataframe(dataframe)