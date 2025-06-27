from __future__ import annotations
from typing import Any, Optional, List

from langchain_community.chat_message_histories.cosmos_db import (
    CosmosDBChatMessageHistory,
)
from langchain_core.messages import (
    messages_to_dict,
)
import logging
from azure.cosmos.exceptions import CosmosHttpResponseError


class CustomCosmosDBChatMessageHistory(CosmosDBChatMessageHistory):
    """
    Customized CosmosDBChatMessageHistory class with support for chat titles.
    """

    def __init__(
        self,
        cosmos_endpoint: str,
        cosmos_database: str,
        cosmos_container: str,
        session_id: str,
        user_id: str,
        title: Optional[str | None] = None,
        credential: Any = None,
        connection_string: Optional[str] = None,
        ttl: Optional[int] = None,
        cosmos_client_kwargs: Optional[dict] = None,
        files: Optional[List[str]] = [],
    ):
        super().__init__(
            cosmos_endpoint,
            cosmos_database,
            cosmos_container,
            session_id,
            user_id,
            credential=credential,
            connection_string=connection_string,
            ttl=ttl,
            cosmos_client_kwargs=cosmos_client_kwargs,
        )
        self.title = title
        self.files = files

    def _load_existing_title(self) -> None:
        """Loads the existing title from Cosmos DB."""
        item = self._container.read_item(
            item=self.session_id, partition_key=self.user_id
        )
        return item["title"]

    def _load_existing_files(self) -> List[str]:
        """Loads filenames from Cosmos DB."""
        try:
            item = self._container.read_item(
                item=self.session_id, partition_key=self.user_id
            )
            if "files" in item:
                return item["files"]
            else:
                return []
        # case: New chat document
        except CosmosHttpResponseError:
            return []

    def upsert_messages(self) -> None:
        if not self._container:
            raise ValueError("Container not initialized")

        item_body = {
            "id": self.session_id,
            "user_id": self.user_id,
            "messages": messages_to_dict(self.messages),
        }
        item_body["title"] = self.title or self._load_existing_title()
        item_body["files"] = self._load_existing_files() + self.files
        self._container.upsert_item(body=item_body)

    def set_title(self, title: str) -> None:
        self.title = title
        self.upsert_messages()

    def set_files(self, files: List[str]) -> None:
        self.files = files
        self.upsert_messages()
