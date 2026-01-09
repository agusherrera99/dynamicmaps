import csv

import logging
logger = logging.getLogger(__name__)

from typing import Optional

import polars as pl

from .map_maker import MapMaker

from ..departamentos import Departamentos
from ..surtidores import Surtidores


class TasaVialMap(MapMaker):
    def __init__(self) -> None:
        super().__init__()
        self.departamentos_data: Optional[dict] = None
        self.surtidores_data: Optional[csv.DictReader] = None

        # Mejorar annotation
        self.merged_data: None = None

        self.set_data()

    def set_data(self) -> None:
        try:
            self.departamentos_data: Optional[dict] = Departamentos().get_data()
            self.surtidores_data: Optional[csv.DictReader] = Surtidores().get_data()
            logger.info("Conjunto de datos configurar correctamente")
        except Exception as error:
            logger.exception(f"Al intentar configurar los conjuntos de datos: {error}")

    # TODO's
    # Decouple conversión de los datos a polars DataFrames en métodos individuales
    # Hacer captura de Exception para el método merge_data
    # Mejorar annotations y añadir logging messages
    def merge_data(self) -> None:
        df_departamentos: None = None
        df_surtidores: None = None

        if self.departamentos_data is not None and self.surtidores_data is not None:
            df_departamentos = pl.DataFrame(self.departamentos_data)
            df_surtidores = pl.DataFrame(self.surtidores_data)

            merged_df = df_departamentos.join(df_surtidores, on="column", how="left")
            if merged_df is not None:
                self.merged_df = merged_df
            else:
                return None
        else:
            return None
