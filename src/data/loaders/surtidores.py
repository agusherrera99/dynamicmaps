import pandas as pd

from pandas.core.frame import DataFrame

from .base_loader import BaseLoader


class SurtidoresLoader(BaseLoader):
    def __init__(self, file_path) -> None:
        super().__init__(file_path)

    def _load_raw_data(self) -> DataFrame:
        return pd.read_csv(self.file_path)
