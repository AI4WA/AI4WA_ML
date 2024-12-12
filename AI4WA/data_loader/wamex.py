from pathlib import Path

import geopandas as gpd
from loguru import logger
from tqdm import tqdm

from AI4WA.utils.api import PlatformAI
from AI4WA.utils.constants import DATA_DIR
from AI4WA.utils.timer import timer


class WAMEXLoader:
    def __init__(self, shapefile_path: Path):
        self.shapefile_path = shapefile_path
        self.platform_api = PlatformAI()

    def load_data(self):
        with timer("Loading shapefile"):
            gdf = gpd.read_file(self.shapefile_path)
        logger.info(f"Loaded {len(gdf)} records from {self.shapefile_path}")
        logger.info(gdf.columns.tolist())

        with timer("Adding spatial data to platform"):
            for idx, row in tqdm(gdf.iterrows(), total=len(gdf)):
                try:
                    # Convert row to dictionary and handle geometry separately
                    row_dict = row.drop("geometry").to_dict()

                    # Create the data dictionary with WKT geometry
                    data = {
                        "file_name": row["TITLE"],
                        "metadata_json": row_dict,  # Now contains all fields except geometry
                        "geometry": row["geometry"].wkt,
                    }

                    self.platform_api.add_spatial_data(data)
                except Exception as e:
                    logger.error(f"Failed to add spatial data for row {idx}")
                    logger.exception(e)


if __name__ == "__main__":
    loader = WAMEXLoader(
        shapefile_path=DATA_DIR / "Exploration_Reports_shp" / "Exploration_Reports.shp"
    )
    loader.load_data()
