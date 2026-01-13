from dataclasses import dataclass, field
from typing import Tuple, List, Optional


@dataclass(frozen=True)
class BaseMapConfig:
    """
    Configuración base para todos los mapas.
    """

    center: Tuple[float, float] = (-37.0, -60.0)
    zoom_start: int = 6

    tiles: str = 'cartodbpositron'

    width: Optional[str] = None
    height: Optional[str] = None

    zoom_control: bool = True
    scrollWheelZoom: bool = True

    def to_folium_kwargs(self) -> dict:
        """
        Convierte la config a kwargs para folium.Map()

        Returns:
            Diccionario de argumentos para folium.Map
        """

        kwargs = {
            'location': list(self.center),
            'zoom_start': self.zoom_start,
            'tiles': self.tiles,
            'zoom_control': self.zoom_control,
            'scrollWheelZoom': self.scrollWheelZoom
        }

        if self.width:
            kwargs['width'] = self.width
        if self.height:
            kwargs['height'] = self.height

        return kwargs

@dataclass(frozen=True)
class ChoroplethConfig:
    """
    Configuración específica para mapas choropleth
    """

    value_column: str
    key_column: str

    fill_color: str = 'YlOrRd'
    fill_opacity: float = 0.7
    line_opacity: float = 0.2
    nan_fill_color: str = 'lightgray'

    legend_name: str = 'Valor'
    bins: Optional[int] = None

    def to_folium_kwargs(self, geo_data, data) -> dict:
        """
        Convierte la config a kwargs para folium.Choropleth

        Args:
            geo_data: GeoDataFrame o dict con geometrías
            data: DataFrame con los datos a mapear

        Returns:
            Diccionario de argumentos para folium.Choropleth
        """

        kwargs = {
            'geo_data': geo_data,
            'data': data,
            'columns': [self.key_column, self.value_column],
            'key_on': f'feature.properties.{self.key_column}',
            'fill_color': self.fill_color,
            'fill_opacity': self.fill_opacity,
            'line_opacity': self.line_opacity,
            'nan_fill_color': self.nan_fill_color,
            'legend_name': self.legend_name
        }

        if self.bins:
            kwargs['bins'] = self.bins

        return kwargs

@dataclass(frozen=True)
class TooltipConfig:
    """
    Configuración para tooltips (información al pasal el mouse)
    """

    fields: List[str] = field(default_factory=list)
    aliases: List[str] = field(default_factory=list)

    style: str = "background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;"

    localize: bool = True

    def __post_init__(self):
        """
        Validación después de la inicialización
        """

        if len(self.fields) != len(self.aliases):
            raise ValueError(
                f"fields y aliases deben tener la misma longitud: "
                f"{len(self.fields)} != {len(self.aliases)}"
            )

    def to_folium_kwargs(self) -> dict:
        """
        Convierte a kwargs para folium.GeoJsonTooltip
        """

        return {
            'fields': self.fields,
            'aliases': self.aliases,
            'localize': self.localize,
            'style': self.style
        }

@dataclass(frozen=True)
class HeatmapConfig:
    """
    Configuración para mapas de calor (heatmap)
    """

    radius: int = 15
    blur: int = 15
    min_opacity: float = 0.5
    max_val: Optional[float] = None

    gradient: dict = field(default_factory=lambda: {
        0.0: 'blue',
        0.5: 'lime',
        0.7: 'yellow',
        1.0: 'red'
    })

    def to_folium_kwargs(self) -> dict:
        """Convierte a kwargs para folium.plugins.HeatMap"""

        kwargs = {
            'radius': self.radius,
            'blur': self.blur,
            'min_opacity': self.min_opacity,
            'gradient': self.gradient
        }

        if self.max_val:
            kwargs['max_val'] = self.max_val

        return kwargs

class MapConfigPresets:
    """
    Presets de configuraciones comunes
    """

    @staticmethod
    def argentina_base() -> BaseMapConfig:
        return BaseMapConfig(
            center=(-37.0, -60.0),
            zoom_start=6,
            tiles='cartodbpositron'
        )

    @staticmethod
    def buenos_aires_provincia() -> BaseMapConfig:
        return BaseMapConfig(
            center=(-36.5, -60.0),
            zoom_start=7,
            tiles='cartodbpositron'
        )

    @staticmethod
    def tasa_vial_choropleth(value_col: str = 'promedio_tasa_vial') -> ChoroplethConfig:
        return ChoroplethConfig(
            value_column=value_col,
            key_column='localidad_norm',
            fill_color='ylOrRd',
            legend_name='Tasa Vial Promedio'
        )

    @staticmethod
    def basic_tooltip(fields: List[str], aliases: List[str]) -> TooltipConfig:
        return TooltipConfig(
            fields=fields,
            aliases=aliases
        )


