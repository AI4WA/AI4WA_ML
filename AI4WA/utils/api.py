import requests
from loguru import logger

from AI4WA.utils.config_reader import ConfigReader
from AI4WA.utils.constants import CONFIG_YAML


class PlatformAI:
    def __init__(self):
        self.config = ConfigReader(CONFIG_YAML).get_config()
        self.api_url = self.config["platform"]["url"]
        self.api_token = self.config["platform"]["token"]
        logger.info(f"PlatformAI initialized with URL: {self.api_url}")
        logger.info(f"PlatformAI initialized with token: {self.api_token}")
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
        }

    def add_spatial_data(self, data):

        response = requests.post(
            f"{self.api_url}/wamex/spatial-metadata/", headers=self.headers, json=data
        )
        if response.status_code == 201:
            logger.info("Spatial data added successfully")
        else:
            logger.error("Failed to add spatial data")
            logger.error(response.text)

    def get_spatial_data_list(self):
        res = requests.get(
            f"{self.api_url}/wamex/spatial-metadata/", headers=self.headers
        )
        if res.status_code == 200:
            return res.json()
        else:
            logger.error("Failed to get spatial data list")
            logger.error(res.text)


if __name__ == "__main__":
    platform_ai = PlatformAI()
    logger.info(f"API URL: {platform_ai.api_url}")
    logger.info(f"API Token: {platform_ai.api_token}")
