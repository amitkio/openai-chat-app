import logging
from typing import List, Optional
from langchain_core.messages import SystemMessage
from core.custom_cosmos_db import CustomCosmosDBChatMessageHistory
from config import app_config
from utils.exceptions import ChatServiceError

logger = logging.getLogger(__name__)


class ChatHistoryService:
    def __init__(self):
        self.cosmos_endpoint = app_config.AZURE_COSMOS_DB_ENDPOINT
        self.cosmos_key = app_config.AZURE_COSMOS_DB_KEY
        self.database_name = app_config.COSMOS_DATABASE_NAME
        self.container_name = app_config.COSMOS_CONTAINER_NAME

    async def get_history_instance(
        self, session_id: str, title: Optional[str] = None, files: List[str] = []
    ) -> CustomCosmosDBChatMessageHistory:
        """
        Fetches CustomCosmosDBChatMessageHistory instance for sessionId (Thread).
        """
        try:
            history = CustomCosmosDBChatMessageHistory(
                cosmos_endpoint=self.cosmos_endpoint,
                credential=self.cosmos_key,
                cosmos_database=self.database_name,
                cosmos_container=self.container_name,
                session_id=session_id,
                user_id=1,  # TODO: Change when auth is added, single user for now
                title=title,
                files=files,
            )
            history.prepare_cosmos()
            logger.info(f"CosmosDB history loaded for session: {session_id}")
            return history
        except Exception as e:
            logger.error(
                f"Failed to initialize CosmosDB history for session {session_id}: {e}",
                exc_info=True,
            )
            raise ChatServiceError(
                status_code=500, detail=f"Database initialization error: {e}"
            )

    async def create_new_chat_history(self) -> CustomCosmosDBChatMessageHistory:
        """Creates a new chat history instance with a new UUID and initial message."""
        from uuid import uuid4

        new_uuid = str(uuid4().int)
        cosmos_history = await self.get_history_instance(
            session_id=new_uuid, title="New Chat"
        )
        cosmos_history.add_message(
            SystemMessage(content="You are a helpful assistant!")
        )
        return cosmos_history

    async def clear_chat_history(self, session_id: str):
        """Clears the chat history for a given session ID."""
        history = await self.get_history_instance(session_id)
        history.clear()
        logger.info(f"Chat history cleared for session: {session_id}")


chat_history_service = ChatHistoryService()
