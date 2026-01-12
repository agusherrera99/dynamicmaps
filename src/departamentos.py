import json

import logging
logger = logging.getLogger(__name__)

from pathlib import PosixPath
from typing import Optional, Union

from .paths import project_path


class Departamentos:
    def __init__(self) -> None:
        self.departamentos_path: PosixPath = project_path.get_departamentos_path()

    def get_data(self) -> Optional[list[dict[str, Union[str, int, float]]]]:
        _list = []
        try:
            with open(self.departamentos_path, 'r') as jsonfile:
                data: dict = json.load(jsonfile)
                features = data.get("features", [])

            for feature in features:
                dept_info = {
                    "partido": feature["properties"]["nam"],
                    "provincia": feature["properties"]["nam_2"],
                    "gid": feature["properties"]["gid"],
                    "in1": feature["properties"]["in1"],
                    "geometry": feature["geometry"]
                }
                _list.append(dept_info)
            logger.info("Datos de departamentos obtenidos correctamente")
            return _list
        except FileNotFoundError:
            logger.exception(f"{self.departamentos_path} no existe")
            return None
        except Exception as error:
            logger.exception(f"Al intentar obtener la información de los departamentos: {error}")
            return None
