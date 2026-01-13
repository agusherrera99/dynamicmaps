import logging

from typing import Optional

import pandas as pd

import folium

from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame

from ..base.map_builder import MapBuilder
from ..base.map_config import (
    BaseMapConfig,
    ChoroplethConfig,
    TooltipConfig,
    MapConfigPresets
)
from ...data.repositories.data_repository import DataRepository

logger = logging.getLogger(__name__)


class TasaVialMap:
    """
    Generador de mapas de Tasa Vial
    """

    def __init__(self, repository: Optional[DataRepository] = None) -> None:
        """
        Args:
            repository: Repository para acceso de datos.
                        Si es None, crea una instancia nueva.
        """

        self.repository = repository or DataRepository()
        self._processed_data: Optional[DataFrame] = None
        logger.debug("TasaVialMap inicializado")

    def _prepare_data(self) -> Optional[DataFrame]:
        """
        Prepara y procesa datos de tasa vial.

        Returns:
            DataFrame procesado o None si falla
        """

        try:
            logger.info("Preparando datos de tasa vial")

            data = self.repository.get_surtidores_por_departamento()
            if data is None:
                logger.error("No se pudieron obtener datos")
                return None

            subset = data.loc[
                :,
                ['periodo', 'localidad_norm', 'tasa_vial', 'producto']
            ].copy()
            subset['tasa_vial'] = (
                subset['tasa_vial']
                .astype(str)
                .str.replace(',', '.', regex=False)
            )
            subset['tasa_vial'] = pd.to_numeric(
                subset['tasa_vial'],
                errors='coerce'
            )

            processed = (
                subset
                .groupby(
                    ['periodo', 'localidad_norm', 'producto'],
                    as_index=False
                )
                .agg(promedio_tasa_vial=('tasa_vial', 'mean'))
            )
            logger.info(
                f"Datos preparados: {len(processed)} registros de "
                f"{subset['periodo'].nunique()} periodos"
            )
            return processed
        except Exception as error:
            logger.exception(f"Error al preparar datos: {error}")

    def _get_processed_data(self, force_reload: bool = False) -> Optional[DataFrame]:
        """
        Obtiene datos procesados con caché local

        Args:
            force_reload: Si True, reprocesa los datos

        Returns:
            DataFrame procesado
        """

        if force_reload or self._processed_data is None:
            self._processed_data = self._prepare_data()
        return self._processed_data

    def _filter_data(
        self,
        periodo: str,
        producto: str
    ) -> Optional[DataFrame]:
        """
        Filtra datos por periodo y producto específico

        Args:
            periodo: Periodo a filtrar (ej: "2024-01")
            producto: Producto a filtrar (ej: "GNC")

        Returns:
            DataFrame filtrado o None si no hay datos
        """

        processed = self._get_processed_data()
        if processed is None:
            return None

        filtered = processed[
            (processed['periodo'] == periodo) &
            (processed['producto'] == producto)
        ]
        if filtered.empty:
            logger.warning(
                f"No hay datos para periodo='{periodo}', producto='{producto}'"
            )
            return None

        logger.info(f"Datos filtrados: {len(filtered)} registros")
        return filtered

    def _merge_with_geodata(self, filtered_data: DataFrame) -> Optional[GeoDataFrame]:
        """
        Combina datos filtrados con geometrías

        Args:
            filtered_data: DataFrame con tasa vial filtrada

        Returns:
            GeoDataFrame combinado o None si falla
        """

        try:
            gdf_departamentos = self.repository.get_departamentos()
            if gdf_departamentos is None:
                logger.error("No se pudieron obtener departamentos")
                return None

            if 'localidad_norm' not in gdf_departamentos.columns:
                gdf_departamentos['localidad_norm'] = (
                    gdf_departamentos['nam']
                    .str.lower()
                    .str.strip()
                )

            merged = gdf_departamentos.merge(
                filtered_data,
                on='localidad_norm',
                how='left'
            )

            logger.info(f"GeoDataFrame combinado: {len(merged)} features")
            return merged
        except Exception as error:
            logger.exception(f"Error al combinar con geodata: {error}")
            return None

    def make_map(
        self,
        periodo: str,
        producto: str,
        base_config: Optional[BaseMapConfig] = None
    ) -> Optional[folium.Map]:
        """
        Crea un mapa de tasa vial para periodo y producto específicos

        Args:
            periodo: Periodo a visualizar (ej: "2024-01")
            producto: Producto a visualizar (ej: "GNC")
            base_config: Configuración base del mapa (opcional)

        Returns:
            Mapa folium o None si falla

        Example:
            >>> mapper = TasaVialMap()
            >>> mapa = mapper.make_map("2024-01", "GNC")
            >>> mapa.save("tasa_vial_2024_01.html")
        """

        try:
            logger.info(
                f"Creando mapa de tasa vial: periodo={periodo}, producto={producto}"
            )

            filtered_data = self._filter_data(periodo, producto)
            if filtered_data is None:
                return None

            map_gdf = self._merge_with_geodata(filtered_data)
            if map_gdf is None:
                return None

            base_cfg = base_config or MapConfigPresets.buenos_aires_provincia()

            choropleth_cfg = ChoroplethConfig(
                value_column='promedio_tasa_vial',
                key_column='localidad_norm',
                fill_color='YlOrRd',
                legend_name=f'Tasa Vial Promedio - {producto} ({periodo})'
            )

            tooltip_cfg = TooltipConfig(
                fields=['localidad_norm', 'promedio_tasa_vial'],
                aliases=['Localidad', 'Tasa Vial Promedio']
            )

            map = (
                MapBuilder()
                .with_base_config(base_cfg)
                .add_choropleth_layer(
                    geo_data=map_gdf,
                    data=map_gdf,
                    config=choropleth_cfg,
                    name='Tasa Vial'
                )
                .add_geojson_layer(
                    geo_data=map_gdf,
                    tooltip_config=tooltip_cfg,
                    name='Tooltips'
                )
                .build()
            )

            logger.info("Mapa creado exitosamente")
            return map
        except Exception as e:
            logger.exception(f"Error al crear mapa: {error}")
            return None

    def get_available_periodos(self) -> list[str]:
        """
        Retorna lista de periodos disponibles en los datos

        Returns:
            Lista ordenada de periodos únicos
        """

        processed = self._get_processed_data()
        if processed is None:
            return []
        return sorted(processed['periodo'].unique().tolist())

    def get_available_productos(self) -> list[str]:
        """
        Retorna lista de productos disponibles en los datos

        Returns:
            Lista ordenada de productos únicos
        """
        processed = self._get_processed_data()
        if processed is None:
            return []
        return sorted(processed['producto'].unique().tolist())

    def clear_cache(self) -> None:
        """Limpia el caché local de datos procesados"""
        self._processed_data = None
        logger.info("Caché local limpiado")
