from azure.cosmos import CosmosClient, PartitionKey
from langchain_community.vectorstores.azure_cosmos_db_no_sql import (
    AzureCosmosDBNoSqlVectorSearch,
)
from langchain_openai import AzureOpenAIEmbeddings

from config import app_config


HOST = app_config.AZURE_COSMOS_DB_ENDPOINT
KEY = app_config.AZURE_COSMOS_DB_KEY


indexing_policy = {
    "indexingMode": "consistent",
    "includedPaths": [{"path": "/*"}],
    "excludedPaths": [{"path": '/"_etag"/?'}],
    "vectorIndexes": [{"path": "/embedding", "type": "diskANN"}],
    "fullTextIndexes": [{"path": "/text"}],
}

vector_embedding_policy = {
    "vectorEmbeddings": [
        {
            "path": "/embedding",
            "dataType": "float32",
            "distanceFunction": "cosine",
            "dimensions": 1536,
        }
    ]
}

full_text_policy = {
    "defaultLanguage": "en-US",
    "fullTextPaths": [{"path": "/text", "language": "en-US"}],
}


cosmos_client = CosmosClient(HOST, KEY)
database_name = app_config.COSMOS_VECTOR_DB_NAME
container_name = app_config.COSMOS_VECTOR_CONTAINER_NAME
partition_key = PartitionKey(path="/id")
cosmos_container_properties = {"partition_key": partition_key}


openai_embeddings = AzureOpenAIEmbeddings(
    model=app_config.OPENAI_EMBEDDINGS_MODEL_NAME,
    chunk_size=1,
    azure_deployment=app_config.OPENAI_EMBEDDINGS_MODEL_DEPLOYMENT,
    openai_api_version=app_config.OPENAI_EMBEDDINGS_API_VERSION,
    azure_endpoint=app_config.AZURE_OPENAI_ENDPOINT,
)


def create_vector_search() -> AzureCosmosDBNoSqlVectorSearch:
    vector_search = AzureCosmosDBNoSqlVectorSearch(
        embedding=openai_embeddings,
        cosmos_client=cosmos_client,
        database_name=database_name,
        container_name=container_name,
        vector_embedding_policy=vector_embedding_policy,
        full_text_policy=full_text_policy,
        indexing_policy=indexing_policy,
        cosmos_container_properties=cosmos_container_properties,
        cosmos_database_properties={},
        full_text_search_enabled=True,
    )

    return vector_search
