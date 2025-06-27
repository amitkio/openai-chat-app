# utils/file_handling.py
import os
import tempfile
import logging
from typing import List, Optional
from fastapi import UploadFile
from core.file_processor import file_processor
from langchain_core.documents import Document
from utils.exceptions import FileProcessingError

logger = logging.getLogger(__name__)


class FileHandler:
    @staticmethod
    async def save_uploaded_file_temporarily(uploaded_file: UploadFile) -> str:
        """
        Saves an uploaded file to a temporary location and returns path.
        """
        if not uploaded_file.filename:
            raise FileProcessingError(
                status_code=400, detail="Uploaded file has no filename."
            )
        if uploaded_file.size == 0:
            raise FileProcessingError(status_code=400, detail="Uploaded file is empty.")

        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=os.path.splitext(uploaded_file.filename)[1]
            ) as temp_file:
                temp_file_path = temp_file.name
                while True:
                    chunk = await uploaded_file.read(8192)
                    if not chunk:
                        break
                    temp_file.write(chunk)
            logger.info(
                f"File '{uploaded_file.filename}' saved temporarily to: {temp_file_path} "
                f"(Size: {os.path.getsize(temp_file_path)} bytes)"
            )
            return temp_file_path
        except Exception as e:
            logger.error(
                f"Error saving temporary file '{uploaded_file.filename}': {e}",
                exc_info=True,
            )
            raise FileProcessingError(
                status_code=500, detail=f"Failed to save file: {e}"
            )

    @staticmethod
    def process_pdf_documents(
        file_path: str, chat_id: str, filename: str
    ) -> List[Document]:
        """
        Processes a PDF file into Langchain documents and adds metadata.
        """
        try:
            documents = file_processor(file_path)
            for doc in documents:
                doc.metadata["chat_id"] = chat_id
                doc.metadata["filename"] = filename
            logger.info(f"Processed {len(documents)} documents from '{filename}'.")
            return documents
        except Exception as e:
            logger.error(f"Error processing PDF '{filename}': {e}", exc_info=True)
            raise FileProcessingError(
                status_code=500, detail=f"Failed to process PDF: {e}"
            )

    @staticmethod
    def cleanup_temporary_file(file_path: Optional[str]):
        """Deletes a temporary file if it exists."""
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Temporary file '{file_path}' cleaned up.")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file '{file_path}': {e}")


file_handler = FileHandler()
