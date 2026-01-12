import logging
logger = logging.getLogger(__name__)

from src.maps import TasaVialMap


def main():
    logging_fmt = '%(asctime)s | %(filename)s.%(funcName)s (line: %(lineno)d) - %(levelname)s: %(message)s'
    logging.basicConfig(
        filename="dynamicmaps.log",
        level=logging.DEBUG,
        format=logging_fmt
    )


if __name__ == "__main__":
    main()
