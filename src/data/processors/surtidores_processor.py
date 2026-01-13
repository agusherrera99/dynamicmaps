import logging

from difflib import SequenceMatcher

from typing import Optional

from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame

logger = logging.getLogger(__name__)


class SurtidoresProcessor:
    def __init__(self) -> None:
        self.similarity_threshold: float = 0.86

    def get_similarity(self, str1: str, str2: str) -> float:
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def find_best_match(self, localidad: str, departamentos: list[str]) -> Optional[str]:
        best_match = None
        best_score = 0

        for dept in departamentos:
            score = self.get_similarity(localidad, dept)
            if score > best_score:
                best_score = score
                best_match = dept

        if best_score >= self.similarity_threshold:
            return best_match
        return None

    def normalize_localidades(self, energia_df: DataFrame, departamentos: list[str]) -> DataFrame:
        energia_df['localidad_norm'] = energia_df['localidad'].str.lower().str.strip()
        no_match = energia_df[
            ~energia_df['localidad_norm'].isin(departamentos)
        ]['localidad_norm'].unique()

        mapped = {}
        for loc in no_match:
            best_match = self.find_best_match(loc, departamentos)
            if best_match:
                mapped[loc] = best_match

        energia_df['localidad_norm'] = energia_df['localidad_norm'].replace(mapped)
        return energia_df

    def merge_with_departamentos(self, surtidores: DataFrame, departamentos: GeoDataFrame) -> Optional[GeoDataFrame]:
        try:
            departamentos['partido_norm'] = departamentos['nam'].str.lower().str.strip()
            surtidores = self.normalize_localidades(surtidores, departamentos)
            merged_gdf: GeoDataFrame = departamentos.merge(
                surtidores,
                left_on='partido_norm',
                right_on='localidad_norm',
                how='inner'
            )
            return merged_gdf
        except Exception as error:
            logger.exception(f"Error: Al mergear datos de surtidores con departamentos: {error}")
            return None
