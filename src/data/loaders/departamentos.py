import geopandas as gpd

from geopandas.geodataframe import GeoDataFrame

from .base_loader import BaseLoader


class DepartamentosLoader(BaseLoader):
    def __init__(self, file_path):
        super().__init__(file_path)

    def _load_raw_data(self) -> GeoDataFrame:
        return gpd.read_file(self.file_path)
