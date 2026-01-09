import csv

import logging
logger = logging.getLogger(__name__)

from pathlib import PosixPath
from typing import Optional

from .paths import ProjectPath


class Surtidores:
    def __init__(self) -> None:
        self.surtidores_path: PosixPath = ProjectPath().get_surtidores_path()

    def get_data(self) -> Optional[csv.DictReader]:
        try:
            with open(self.surtidores_path, newline='') as csvfile:
                surtidores_reader: csv.DictReader = csv.reader(csvfile, delimiter=',', quotechar='|')
                logger.info("Datos de surtidores obtenidos correctamente.")
                return surtidores_reader
        except FileNotFoundErorr:
            logger.exception(f"{self.surtidores_path} no existe")
            return None
        except json.JSONDecodeError as error:
            logger.exception(f"Al intentar decodificar el archivo JSON - {error}")
            return None
        except Exception as error:
            logger.exception(f"Al intentar obtener los datos de los surtidores - {error}")
            return None
