from pathlib import Path, PosixPath

class ProjectPath:
    def __init__(self) -> None:
        self.paths: PosixPath = Path(__file__).resolve()
        self.root_path: PosixPath = self.paths.parent.parent
        self.src_path: PosixPath = self.root_path / "src"

        self.csvs_path: PosixPath = self.root_path / "csvs"
        self.geopackages_path: PosixPath = self.root_path / "geopackages"
        self.parquets_path: PosixPath = self.root_path / "parquets"

        self.surtidores_path: PosixPath = self.csvs_path / "surtidores_buenos_aires.csv"
        self.departamentos_path: PosixPath = self.geopackages_path / "departamentos_buenos_aires.geojson"

        self.surtidores_departamentos_path: PosixPath = self.parquets_path / "surtidores_departamentos_buenos_aires.parquet"

    def get_surtidores_path(self) -> PosixPath:
        return self.surtidores_path

    def get_departamentos_path(self) -> PosixPath:
        return self.departamentos_path

    def get_surtidores_departamentos_path(self) -> PosixPath:
        return self.surtidores_departamentos_path

project_path = ProjectPath()
