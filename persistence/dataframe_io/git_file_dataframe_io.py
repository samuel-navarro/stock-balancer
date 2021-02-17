import os
from pathlib import Path
from contextlib import contextmanager
import subprocess as sp
from typing import Sequence

import pandas as pd

from persistence import PersistenceDataFrameIO, FileDataFrameIO


@contextmanager
def _switch_directory_to(path: str):
    previous_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous_dir)


class GitFileDataFrameIO(PersistenceDataFrameIO):
    def __init__(self, file_path: str, ssh_private_key_path: str):
        self._file_path = Path(file_path).resolve()
        self._ssh_key_path = Path(ssh_private_key_path).resolve()
        self._file_dataframe_io = FileDataFrameIO(file_path)

    def read_dataframe(self) -> pd.DataFrame:
        self._reset_to_master()
        return self._file_dataframe_io.read_dataframe()

    def save_dataframe(self, dataframe: pd.DataFrame):
        self._reset_to_master()
        self._file_dataframe_io.save_dataframe(dataframe)
        self._run_git(['git', 'add', self._file_path.name])
        self._run_git(['git', 'commit', '-m', f'stock-balancer: Updated {self._file_path.name}'])

    def _reset_to_master(self):
        self._run_git('git fetch -p'.split())
        self._run_git('git reset --hard origin/master'.split())

    def _run_git(self, command: Sequence[str]):
        repo_path = self._file_path.parent
        with _switch_directory_to(str(repo_path)):
            return sp.run(command,
                          env={'GIT_SSH_COMMAND': f'ssh -i {self._ssh_key_path}'},
                          capture_output=True,
                          check=True)
