import logging

from typing import Optional, Dict, Any
from functools import lru_cache

import pandas as pd
import geopandas as gpd

from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame

logger = logging.getLogger(__name__)


class  DataRepository:
    """
    Repositorio singleton para acceso centralizado de datos
    """

    _instance: Optional['DataRepository'] = None

    def __new__(cls) -> 'DataRepository':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """
        Esta inicialización ocurre una sola vez.
        Evita re-inicializar en llamadas susecuentes
        """

        if self._initialized:
            return

        self._cache: Dict[str, Any] = {}
        self._initialized = True
        logger.info("DataRepository inicializado")

    def get_surtidores(self, force_reload: bool = False) -> Optional[DataFrame]:
        """
        Obtiene datos de surtidores con caché automatico

        Args:
            force_reload: Si True, recarga ignorando caché

        Returns:
            DataFrame con datos de surtidores o None si falla
        """

        cache_key = "surtidores"

        if not force_reload and cache_key in self._cache:
            logger.debug(f"Retornado {cache_key} desde caché")
            return self._cache[cache_key]

        try:
            from ..loaders.surtidores import SurtidoresLoader
            from ...paths import project_path

            loader = SurtidoresLoader(project_path.get_surtidores_path())
            data = loader.load()

            if data is not None:
                self._cache[cache_key] = data

            return data
        except Exception as error:
            logger.exception(f"Error al obtener surtidores: {error}")
            return None

    def get_departamentos(self, force_reload: bool = False) -> Optional[GeoDataFrame]:
        """
        Obtiene datos geográficos de departamentos

        Args:
            force_reload: Si True, recarga ignorando caché

        Returns:
            GeoDataFrame con geometrías de departamentos
        """

        cache_key = "departamentos"

        if not force_reload and cache_key in self._cache:
            logger.debug(f"Retornando {cache_key} desde caché")
            return self._cache[cache_key]
        
        try:
            from ..loaders.departamentos import DepartamentosLoader
            from ...paths import project_path

            loader = DepartamentosLoader(project_path.get_departamentos_path())
            data = loader.load()

            if data is not None:
                self._cache[cache_key] = data

            return data
        except Exception as error:
            logger.exception(f"Error al obtener departamentos: {error}")
            return None

    def get_surtidores_por_departamento(
        self,
        force_reload: bool = False
    ) -> Optional[GeoDataFrame]:
        """
        Obtiene datos combinados de surtidores y departamentos

        Args:
            force_reload: Si True, recarga ignorando caché

        Returns:
            GeoDataFrame combinado o None si falla
        """

        cache_key = "surtidores_departamentos"

        if not force_reload and cache_key in self._cache:
            logger.debug(f"Retornando {cache_key} desde caché")
            return self._cache[cache_key]

        try:
            from ..processors.surtidores_processor import SurtidoresProcessor
            surtidores = self.get_surtidores(force_reload)
            departamentos = self.get_departamentos(force_reload)

            if surtidores is None or departamentos is None:
                logger.warning("No se pudieron cargar datos base")
                return None

            processor = SurtidoresProcessor()
            merged = processor.merge_with_departamentos(surtidores, departamentos)

            if merged is not None:
                self._cache[cache_key] = merged
            return merged
        except Exception as error:
            logger.exception(f"Error al combinar datos: {error}")
            return None

def clear_cache(self, key: Optional[str] = None) -> None:
    """
    Limpia el caché de datos

    Args:
        key: Si se especifica, limpia solo esa entrada.
            Si es None, limpia todo el caché
    """

    if key:
        self._cache.pop(keu, None)
        logger.info(f"Caché limpiado para: {key}")
    else:
        self._cache.clear()
        logger.info(f"Caché completo limpiado")

def get_cache_info(self) -> Dict[str, int]:
    """
    Retorna información sobre el estado del caché

    Returns:
        Diccionario con las keys cacheadas y tamaño en memoria
    """

    info = {}
    for key, value in self._cache.items():
        if isinstance(value, (DataFrame, GeoDataFrame)):
            size_mb = value.memory_usage(deep=True).sum() / (1024 * 1024)
            info[key] = f"{size_mb:.2f} MB"
        else:
            info[key] = "unknown size"
    return info






