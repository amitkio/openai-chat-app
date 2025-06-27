import logging
from typing import List, Tuple
from langchain_community.vectorstores.azure_cosmos_db_no_sql import (
    PreFilter,
    Condition,
)
from langchain_core.documents import Document

from core.vector_stores import create_vector_search

logger = logging.getLogger(__name__)


class VectorStoreService:
    def __init__(self):
        self.vector_search = create_vector_search()

    def similarity_search_with_filter(
        self, query: str, chat_id: str, k: int = 3
    ) -> List[Tuple[Document, float]]:
        """
        Performs a similarity search with a pre-filter for a specific chat_id.
        """
        id_filter = PreFilter(
            conditions=[
                Condition(
                    property="metadata.chat_id",
                    operator="$eq",
                    value=str(chat_id),
                )
            ]
        )
        documents_with_scores = self.vector_search.similarity_search_with_score(
            query=query, k=k, pre_filter=id_filter
        )
        logger.debug(
            f"Found {len(documents_with_scores)} documents for chat ID {chat_id}"
        )
        return documents_with_scores

    async def add_documents_to_vector_store(self, documents: List[Document]):
        """Adds documents to the vector store."""
        await self.vector_search.aadd_documents(documents=documents)
        logger.info(f"Added {len(documents)} documents to vector store.")

    def delete_documents_by_id(self, doc_ids: List[str]):
        """Deletes documents from the vector store by their IDs."""
        if doc_ids:
            self.vector_search.delete(doc_ids)
            logger.info(f"Deleted {len(doc_ids)} documents from vector store.")
        else:
            logger.info("No document IDs provided for deletion.")


vector_store_service = VectorStoreService()
