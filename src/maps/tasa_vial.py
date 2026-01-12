import logging
logger = logging.getLogger(__name__)

from .map_maker import MapMaker
from ..surtidores_departamentos import SurtidoresDepartamentos


class TasaVialMap(MapMaker):
    def __init__(self):
        super().__init__()
