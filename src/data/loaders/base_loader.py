import logging

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BaseLoader(ABC):
    """
    Clase base abstracta para cargadores de datos.

    Define el esqueleto del algoritmo de carga, delegando pasos específicos a los subclases.
    """

    def __init__(self, file_path: Path) -> None:
        """
        Args:
            file_path: Ruta al archivo de datos
        """
        
        self.file_path = file_path
        self._validate_path()

    def _validate_path(self) -> None:
        """Valida que el archivo existe y es accesible"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.file_path}")

        if not self.file_path.is_file():
            raise ValueError(f"La ruta no es un archivo: {self.file_path}")

    def load(self) -> Optional[Any]:
        """
        Orquesta la carga de datos.

        Returns:
            Datos cargados o None si falla
        """

        try:
            logger.info(f"Cargando datos desde {self.file_path.name}")

            raw_data = self._load_raw_data()
            validate_data = self._validate_data(raw_data)

            logger.info(f"Datos cargados exitosamente desde {self.file_path.name}")
            return validate_data
        except Exception as error:
            logger.exception(f"Error al cargar {self.file_path.name}: {error}")
            return None

    @abstractmethod
    def _load_raw_data(self) -> Any:
        """
        Returns:
            Datos crudos sin procesar
        """
        pass

    def _validate_data(self, data: Any) -> Any:
        """
        Método opcional para validar datos después de cargar.

        Args:
            data: Datos crudos cargados

        Returns:
            Datos validados
        """
        return data
