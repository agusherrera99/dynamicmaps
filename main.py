import logging
logger = logging.getLogger(__name__)

from src.maps.composers import TasaVialMap
from src.paths import project_path


def main():
    logging_fmt = '%(asctime)s | %(filename)s.%(funcName)s (line: %(lineno)d) - %(levelname)s: %(message)s'
    logging.basicConfig(
        filename="dynamicmaps.log",
        level=logging.DEBUG,
        format=logging_fmt
    )

    mapper = TasaVialMap()

    print("Periodos disponibles:", mapper.get_available_periodos())
    print("Productos disponibles:", mapper.get_available_productos())

    periodo = "2025/11"
    producto = "GNC"
    map = mapper.make_map(periodo, producto)
    if map:
        map.save(project_path.get_visualizations_path() / f"tasa_vial_{periodo.replace('/', '-')}_{producto}_map.html")
        print("Mapa guardado exitosamente")

if __name__ == "__main__":
    main()
