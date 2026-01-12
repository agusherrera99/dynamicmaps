import logging
logger = logging.getLogger(__name__)

from typing import Optional, Union
from difflib import SequenceMatcher

import geopandas as gpd
import pandas as pd

from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame

from .departamentos import Departamentos
from .paths import project_path
from .surtidores import Surtidores


class SurtidoresDepartamentos():
    def __init__(self) -> None:
        super().__init__()
        self.merged_gdf: Optional[GeoDataFrame] = None
        self.similarity_threshold: float = 0.86

    def get_similarity(self, str1: str, str2: str) -> float:
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def find_best_macth(self, localidad: str, departamentos_list: list[str]) -> Optional[str]:
        best_match = None
        best_score = 0

        for departamento in departamentos_list:
            score = self.get_similarity(localidad, departamento)
            if score > best_score:
                best_score = score
                best_match = departamento

        if best_score >= self.similarity_threshold:
            logger.info(f"Match encontrado: '{localidad}' -> '{best_match}' (similitud: {best_score:.2f})")
            return best_match
        return None

    def normalize_localidades(self, df_energia: DataFrame, departamentos_list: list[str]) -> DataFrame:
        df_energia["localidad_norm"] = df_energia["localidad"].str.lower().str.strip()

        localidades_sin_match = df_energia[
            ~df_energia["localidad_norm"].isin(departamentos_list)
        ]["localidad_norm"].unique()
        logger.info(f"Encontradas {len(localidades_sin_match)} localidades sin match exacto")

        mapped = {}
        for localidad in localidades_sin_match:
            best_match = self.find_best_macth(localidad, departamentos_list)
            if best_match:
                mapped[localidad] = best_match
        logger.info(f"Se crearon {len(mapped)} mapeos por similitud")

        df_energia["localidad_norm"] = df_energia["localidad_norm"].replace(mapped)
        return df_energia

    def merge_data(self) -> None:
        try:
            df_energia: DataFrame = pd.read_csv(Surtidores().surtidores_path)
            gdf_departamentos: GeoDataFrame = gpd.read_file(Departamentos().departamentos_path)

            gdf_departamentos["partido_norm"] = gdf_departamentos["nam"].str.lower().str.strip()
            departamentos_list = gdf_departamentos["partido_norm"].unique().tolist()

            df_energia = self.normalize_localidades(df_energia, departamentos_list)

            self.merged_gdf: Optional[GeoDataFrame] = gdf_departamentos.merge(
                df_energia,
                left_on="partido_norm",
                right_on="localidad_norm",
                how="inner"
            )
            logger.info(f"GeoDataFrame mergeado con éxito. Registros: {len(self.merged_gdf)}")
        except Exception as error:
            logger.exception(f"Al intentar combinar datos en un solo GeoDataFrame - {error}")

    def save_data(self) -> None:
        try:
            self.merge_data()
            if self.merged_gdf is not None and not self.merged_gdf.empty:
                self.merged_gdf.to_parquet(
                    project_path.get_surtidores_departamentos_path()
                )
                logger.info("surtidores_departamentos guardado con éxito.")
            else:
                logger.warning("No hay datos para guardar después del merge")
        except Exception as error:
            logger.exception(f"Al intentar guardar datos de energia por departamentos - {error}")

    def get_data(self) -> Optional[GeoDataFrame]:
        logger.info("obteniendo datos de SurtidoresDepartamentos...")
        try:
            if not project_path.get_surtidores_departamentos_path().exists():
                self.save_data()
            data: GeoDataFrame = gpd.read_parquet(project_path.get_surtidores_departamentos_path())
            logger.info("Datos de SurtidoresDepartamentos obtenidos correctamente.")
            return data
        except Exception as error:
            logger.exception(f"Al intentar obtener la información de surtidores_departamentos - {error}")
            return None
