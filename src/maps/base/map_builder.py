import logging
from typing import Optional, List, Dict, Any

import folium
import geopandas as gpd

from pandas.core.frame import DataFrame
from geopandas.geodataframe import GeoDataFrame

from .map_config import (
    BaseMapConfig,
    ChoroplethConfig,
    TooltipConfig,
    HeatmapConfig,
    MapConfigPresets
)

logger = logging.getLogger(__name__)


class MapBuilder:
    """
    Constructor fluido de mapas Folium
    """

    def __init__(self) -> None:
        self._base_config: BaseMapConfig = MapConfigPresets.argentina_base()
        self._map: Optional[folium.Map] = None
        self._layers: List[Dict[str, Any]] = []

        logger.debug("MapBuilder inicializado")

    def with_base_config(self, config: BaseMapConfig) -> 'MapBuilder':
        """
        Configra el mapa base

        Args:
            config: Configuración base del mapa

        Returns:
            self para encadenamiento
        """

        self._base_config = config
        logger.debug(f"Base config establecida: {config}")
        return self

    def add_choropleth_layer(
        self,
        geo_data: GeoDataFrame,
        data: DataFrame,
        config: ChoroplethConfig,
        name: Optional[str] = None
    ) -> 'MapBuilder':
        """
        Agrega una capa de choropleth

        Args:
            geo_data: GeoDataFrame con geometrías
            data: DataFrame con valores a mapear
            config: Configuración del choropleth
            name: Nombre opcional de la capa

        Returns:
            self para encadenamiento
        """

        self._layers.append({
            'type': 'choropleth',
            'geo_data': geo_data,
            'data': data,
            'config': config,
            'name': name or 'Choropleth Layer'
        })
        logger.debug(f"Capa choropleth agregada: {name}")
        return self

    def add_geojson_layer(
        self,
        geo_data :GeoDataFrame,
        tooltip_config: Optional[TooltipConfig] = None,
        style_function: Optional[callable] = None,
        name: Optional[str] = None
    ) -> 'MapBuilder':
        """
        Agrega una capa GeoJSON con tooltips opcionales

        Args:
            geo_data: GeoDataFrame con geometrías
            tooltip_config: Configuración de tooltip
            style_function: Función para estilizar features
            name: Nombre de la capa

        Returns:
            self para encadenamiento
        """

        self._layers.append({
            'type': 'geojson',
            'geo_data': geo_data,
            'tooltip_config': tooltip_config,
            'style_function': style_function,
            'name': name or 'GeoJSON layer'
        })
        logger.debug(f"Capa GeoJSON agregada: {name}")
        return self

    def add_heatmap_layer(
        self,
        data: List[List[float]],
        config: HeatmapConfig,
        name: Optional[str] = None
    ) -> 'MapBuilder':
        """
        Agrega una copa de mapa de calor

        Args:
            data: Lista de [lat, lon, weight] o [lat, lon]
            config: Configuración del heatmap
            name: Nombre de la capa

        Returns:
            self para encadenamiento
        """

        self._layers.append({
            'type': 'heatmap',
            'data': data,
            'config': config,
            'name': name or 'Heatmap Layer'
        })
        logger.debug(f"Capa heatmap agregada: {name}")
        return self

    def add_marker_cluster(
        self,
        locations: List[tuple],
        popups: Optional[List[str]] = None,
        icons: Optional[List[folium.Icon]] = None,
        name: Optional[str] = None
    ) -> 'MapBuilder':
        """
        Agrega un cluster de marcadores

        Args:
            locations: Lista de (lat, lon)
            popups: Textos para popups (opcional)
            icons: Iconos personalizados (opcional)
            name: Nombre del cluster

        Returns:
            self para encadenamiento
        """

        self._layers.append({
            'type': 'marker_cluster',
            'locations': locations,
            'popups': popups or [None] * len(locations),
            'icons': icons or [None] * len(locations),
            'name': name or 'Marker Cluster'
        })
        logger.debug(f"Marker cluster agregado: {name}")
        return self

    def _create_base_map(self) -> folium.Map:
        """
        Crea el mapa base

        Returns:
            Mapa folium configurado
        """

        logger.info("Creando mapa base")
        return folium.Map(**self._base_config.to_folium_kwargs())

    def _build_choropleth(self, layer_info: Dict[str, Any]) -> None:
        """
        Construye y agrega la capa choropleth al mapa

        Args:
            layer_info: Diccionario con info de la capa
        """

        try:
            config: ChoroplethConfig = layer_info['config']
            geo_data = layer_info['geo_data']
            data = layer_info['data']

            if isinstance(geo_data, GeoDataFrame):
                geo_data = geo_data.__geo_interface__

            choropleth = folium.Choropleth(
                **config.to_folium_kwargs(geo_data, data)
            )
            choropleth.add_to(self._map)
            logger.info(f"Capa choropleth '{layer_info['name']}' agregada")
        except Exception as error:
            logger.exception(f"Error al construir choropleth: {error}")
            raise

    def _build_geojson(self, layer_info: Dict[str, Any]) -> None:
        """
        Construye y agrega una capa GeoJSON

        Args:
            layer_info: Diccionario con info de la capa
        """

        try:
            geo_data = layer_info['geo_data']
            tooltip_config = layer_info.get('tooltip_config')
            style_function = layer_info.get('style_function')

            geojson_kwargs = {}

            if tooltip_config:
                geojson_kwargs['tooltip'] = folium.GeoJsonTooltip(
                    **tooltip_config.to_folium_kwargs()
                )

            if style_function:
                geojson_kwargs['style_function'] = style_function

            geojson = folium.GeoJson(geo_data, **geojson_kwargs)
            geojson.add_to(self._map)
            logger.info(f"Capa GeoJSON '{layer_info['name']}' agregada")
        except Exception as error:
            logger.exception(f"Error al construir GeoJSON: {error}")
            raise

    def _build_heatmap(self, layer_info: Dict[str, Any]) -> None:
        """
        Construye y agrega una capa heatmap

        Args:
            layer_info: Diccionario con info de la capa
        """

        try:
            from folium.plugins import HeatMap

            data = layer_info['data']
            config: HeatmapConfig = layer_info['config']

            heatmap = HeatMap(data, **config.to_folium_kwargs())
            heatmap.add_to(self._map)
            logger.info(f"Capa heatmap '{layer_info['name']}' agregada")
        except Exception as error:
            logger.exception(f"Error al construir heatmap: {error}")
            raise

    def _build_marker_cluster(self, layer_info: Dict[str, Any]) -> None:
        """
        Construye y agrega un cluster de marcadores

        Args:
            layer_info: Diccionario con info de la capa
        """

        try:
            from folium.plugins import MarkerCluster

            locations = layer_info['locations']
            popups = layer_info['popups']
            icons = layer_info['icons']

            marker_cluster = MarkerCluster()

            for loc, popup, icon in zip(locations, popups, icons):
                marker_kwargs = {'location': loc}
                if popup:
                    marker_kwargs['popup'] = popup
                if icon:
                    marker_kwargs['icon'] = icon

                folium.Marker(**marker_kwargs).add_to(marker_cluster)
            marker_cluster.add_to(self._map)
            logger.info(f"Marker Cluster '{layer_info['name']}' agregado")
        except Exception as error:
            logger.exception(f"Error al construir marker cluster: {error}")
            raise

    def build(self) -> folium.Map:
        """
        Construye el mapa final con todas las capas agregadas

        Returns:
            Mapa folium completamente construido

        Raises:
            ValueError: Si no hay capas para construir
        """

        if not self._layers:
            raise ValueError("No hay capas para construir. Agrega al menos una capa.")

        logger.info(f"Construyendo mapa con {len(self._layers)} capas(s)")

        self._map = self._create_base_map()

        for layer in self._layers:
            layer_type = layer['type']

            if layer_type == 'choropleth':
                self._build_choropleth(layer)
            elif layer_type == 'geojson':
                self._build_geojson(layer)
            elif layer_type == 'heatmap':
                self._build_heatmap(layer)
            elif layer_type == 'marker_cluster':
                self._build_marker_cluster(layer)
            else:
                logger.warning(f"Tipo de capa desconocido: {layer_type}")

        logger.info("Mapa construido exitosamente")
        return self._map

    def reset(self) -> 'MapBuilder':
        """
        Resetea el builder a su estado inicial

        Returns:
            self para encadenamiento
        """

        self._base_config = MapConfigPresets.argentina_base()
        self._map = None
        self._layers = []
        logger.debug("Builder reseteado")
        return self
