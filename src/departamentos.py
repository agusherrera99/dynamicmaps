import json

import logging
logger = logging.getLogger(__name__)

from pathlib import PosixPath
from typing import Optional

from .paths import ProjectPath


class Departamentos:
    def __init__(self) -> None:
        self.departamentos_path: PosixPath = ProjectPath().get_departamentos_path()

    def get_data(self) -> Optional[dict]:
        try:
            with open(self.departamentos_path, 'r') as jsonfile:
                data: dict = json.load(jsonfile)
                logger.info("Datos de departamentos obtenidos correctamente")
                return data
        except FileNotFoundError:
            logger.exception(f"{self.departamentos_path} no existe")
            return None
        except Exception as error:
            logger.exception(f"Al intentar obtener la información de los departamentos: {error}")
            return None
