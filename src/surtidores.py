import logging
logger = logging.getLogger(__name__)

import pandas as pd

from pandas.core.frame import DataFrame

from pathlib import PosixPath
from typing import Optional

from .paths import ProjectPath


class Surtidores:
    def __init__(self) -> None:
        self.surtidores_path: PosixPath = ProjectPath().get_surtidores_path()

    def get_data(self) -> DataFrame:
        try:
            data: DataFrame = pd.read_csv(self.surtidores_path)
            logger.info("Datos de surtidores obtenidos correctamente.")
            return data
        except FileNotFoundError:
            logger.exception(f"{self.surtidores_path} no existe")
            return None
        except json.JSONDecodeError as error:
            logger.exception(f"Al intentar decodificar el archivo JSON - {error}")
            return None
        except Exception as error:
            logger.exception(f"Al intentar obtener los datos de los surtidores - {error}")
            return None
