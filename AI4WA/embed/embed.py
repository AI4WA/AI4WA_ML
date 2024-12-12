from fastembed import TextEmbedding
from loguru import logger
from qdrant_client import QdrantClient, models

from AI4WA.utils.api import PlatformAI
from AI4WA.utils.config_reader import ConfigReader
from AI4WA.utils.constants import CONFIG_YAML


class Embedding:
    def __init__(self):
        self.config = ConfigReader(CONFIG_YAML).get_config()
        self.platform_api = PlatformAI()

        self.embedding_model = TextEmbedding()
        self.qdrant_client = QdrantClient(
            url=self.config["qdrant"]["url"],
            port=self.config["qdrant"]["port"],
        )
        self.init_collection("wamex")

    def run(self):
        spatial_data_list = self.platform_api.get_spatial_data_list()
        logger.info(len(spatial_data_list["results"]))

        for spatial_data in spatial_data_list["results"]:
            json_str = str(spatial_data["metadata_json"])
            logger.info(json_str)
            embedding_vector = self.embed(json_str)
            logger.info(embedding_vector)
            self.upsert(embedding_vector, spatial_data)

    def upsert(self, embedding_vector, spatial_data):
        try:
            operation = models.PointStruct(
                id=spatial_data["id"],  # Make sure this is an integer or string
                vector=embedding_vector.tolist(),  # Convert numpy array to list if needed
                payload=spatial_data,
            )

            self.qdrant_client.upload_points(
                collection_name="wamex",
                points=[operation],
                wait=True,  # Wait for the operation to complete
            )
            logger.info(f"Successfully uploaded point with ID {spatial_data['id']}")
        except Exception as e:
            logger.error(f"Error uploading point: {e}")

    def init_collection(self, collection_name):
        """
        Initialize a collection in Qdrant
        :param collection_name: Name of the collection
        :return: None
        """
        # get the existing collections, if exists, skip
        collections = self.qdrant_client.get_collections()
        for collection in collections:
            logger.info(collection[1][0].name)
            if collection[1][0].name == collection_name:
                logger.info(f"Collection {collection_name} already exists")
                return

        self.qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=384, distance=models.Distance.COSINE
            ),
        )

    def embed(self, embed_text: str):
        embed_generator = self.embedding_model.embed([embed_text])
        return list(embed_generator)[0]


if __name__ == "__main__":
    embedding = Embedding()
    # text = "This is a test"
    # embedding_vector = embedding.embed(text)
    # logger.info(embedding_vector)
    embedding.run()
