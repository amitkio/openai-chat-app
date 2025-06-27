import os
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()


class Config:
    AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")
    AZURE_COSMOS_DB_ENDPOINT = os.environ.get("AZURE_COSMOS_DB_ENDPOINT")
    AZURE_COSMOS_DB_KEY = os.environ.get("AZURE_COSMOS_DB_KEY")
    COSMOS_DATABASE_NAME = "chat_messages_db"
    COSMOS_CONTAINER_NAME = "chat_messages_container"
    COSMOS_VECTOR_DB_NAME = "langchain_python_db"
    COSMOS_VECTOR_CONTAINER_NAME = "langchain_python_container"

    OPENAI_EMBEDDINGS_MODEL_NAME = os.environ.get(
        "OPENAI_EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002"
    )
    OPENAI_EMBEDDINGS_MODEL_DEPLOYMENT = os.environ.get(
        "OPENAI_EMBEDDINGS_MODEL_DEPLOYMENT", "text-embedding-ada-002"
    )
    OPENAI_EMBEDDINGS_API_VERSION = os.environ.get(
        "OPENAI_EMBEDDINGS_API_VERSION", "2024-12-01-preview"
    )


app_config = Config()
