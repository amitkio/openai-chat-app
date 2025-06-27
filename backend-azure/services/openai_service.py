import logging
import asyncio
from typing import AsyncGenerator, List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from core.custom_cosmos_db import CustomCosmosDBChatMessageHistory
from config import app_config
from utils.exceptions import OpenAIError

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.model = AzureChatOpenAI(
            azure_endpoint=app_config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=app_config.AZURE_OPENAI_DEPLOYMENT_NAME,
            openai_api_version=app_config.AZURE_OPENAI_API_VERSION,
            temperature=0.8,
            streaming=True,
        )
        self.title_model = AzureChatOpenAI(
            azure_endpoint=app_config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=app_config.AZURE_OPENAI_DEPLOYMENT_NAME,
            openai_api_version=app_config.AZURE_OPENAI_API_VERSION,
            temperature=0.5,
            streaming=False,
        )

    async def generate_response_stream(
        self, prompt: str, chat_history: CustomCosmosDBChatMessageHistory, context: str
    ) -> AsyncGenerator[str, None]:
        """
        Generates a streaming response from OpenAI based on prompt, chat history, and context.
        """
        system_prompt_template = (
            "You are a helpful AI assistant. Answer the user's questions based on the provided context if available, otherwise feel free to use your knowledge."
            f"\n\nContext: {context}"
        )
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system_prompt_template),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessage(content=prompt),
            ]
        )

        chain = (
            RunnablePassthrough.assign(
                chat_history=RunnableLambda(lambda x: chat_history.messages),
            )
            | prompt_template
            | self.model
        )

        try:
            async for chunk in chain.astream({"input": prompt}):
                if chunk.content:
                    yield chunk.content.encode("utf-8")
                    await asyncio.sleep(0.05)
        except Exception as e:
            logger.error(f"Error during AI streaming: {e}", exc_info=True)
            raise OpenAIError(
                status_code=500, detail=f"Error generating AI response: {e}"
            )

    async def generate_chat_title(self, prompt: str) -> str:
        title_prompt: List[BaseMessage] = [
            SystemMessage(
                content=(
                    "You are an AI assistant specialized in summarizing conversations."
                    "Your task is to create a very concise, descriptive, and relevant title "
                    "for the given chat message history. The title should be under 10 words "
                    "and capture the main topic or purpose of the conversation."
                    "Focus on the core subject discussed."
                    "\n\nExamples:"
                    "\n- Chat about Azure Deployment"
                    "\n- LangChain Setup Guide"
                    "\n- Project Feedback Discussion"
                    "\n- Cosmos DB Integration Tips"
                )
            ),
            HumanMessage(
                content=f"Based on the following prompt: '{prompt}', generate a concise title:"
            ),
        ]
        try:
            title_response = await self.title_model.ainvoke(title_prompt)
            return title_response.content
        except Exception as e:
            logger.error(f"Error generating chat title: {e}", exc_info=True)
            raise OpenAIError(
                status_code=500, detail=f"Error generating chat title: {e}"
            )


openai_service = OpenAIService()
