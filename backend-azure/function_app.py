import azure.functions as func
from azurefunctions.extensions.http.fastapi import (
    Request,
    Response,
    StreamingResponse,
    JSONResponse,
)
from fastapi import HTTPException, UploadFile
import json
import logging
import os


from config import app_config
from services.chat_history import chat_history_service
from services.openai_service import openai_service
from services.vector_store import vector_store_service
from utils.file_handling import file_handler
from utils.exceptions import ChatServiceError, FileProcessingError, OpenAIError


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="request_gpt", methods=[func.HttpMethod.POST])
async def stream_openai_text(req: Request) -> StreamingResponse:
    logging.info("Received request for /request_gpt")
    try:
        body = await req.json()
        prompt = body.get("q")
        chat_id_raw = body.get("chatId")

        if not prompt:
            raise HTTPException(
                status_code=400,
                detail="Query parameter 'q' (prompt) is required in the request body.",
            )
        if chat_id_raw is None:
            raise HTTPException(
                status_code=400,
                detail="Query parameter 'chatId' is required in the request body.",
            )

        chat_id = str(chat_id_raw)
        logging.info(
            f"Processing request for chat ID: {chat_id}, prompt: '{prompt[:75]}{'...' if len(prompt) > 75 else ''}'"
        )

        history = await chat_history_service.get_history_instance(chat_id)

        documents_with_scores = vector_store_service.similarity_search_with_filter(
            query=prompt, chat_id=chat_id, k=3
        )
        context = ""
        for document, score in documents_with_scores:
            context += f"content: {document.model_dump_json()}, score: {score}\n\n"

        history.add_user_message(prompt)

        if len(history.messages) == 2:
            try:
                title = await openai_service.generate_chat_title(prompt)
                history.set_title(title=title)
                logging.info(f"Generated and set title for chat {chat_id}: '{title}'")
            except OpenAIError as e:
                logging.warning(
                    f"Could not generate chat title for {chat_id}: {e.detail}"
                )

        full_gpt_response = ""

        async def stream_generator():
            nonlocal full_gpt_response
            try:
                async for chunk in openai_service.generate_response_stream(
                    prompt, history, context
                ):
                    yield chunk
            except OpenAIError as e:
                logging.error(
                    f"Error during AI streaming for chat {chat_id}: {e.detail}",
                    exc_info=True,
                )
                yield f"data: ERROR: An error occurred during response generation: {e.detail}\n\n".encode(
                    "utf-8"
                )
                raise

        async def final_stream_processor():
            nonlocal full_gpt_response
            response_chunks = []
            try:
                async for chunk in stream_generator():
                    response_chunks.append(chunk.decode("utf-8"))
                    yield chunk
                full_gpt_response = "".join(response_chunks)
            except Exception as e:
                pass
            finally:
                if full_gpt_response:
                    history.add_ai_message(full_gpt_response)
                    logging.info(
                        f"Full AI response saved to history for chat {chat_id}."
                    )
                else:
                    logging.warning(
                        f"No AI response generated for chat {chat_id} to save to history."
                    )

        return StreamingResponse(
            final_stream_processor(), media_type="text/event-stream"
        )

    except HTTPException as http_exc:
        logging.error(f"HTTP Error: {http_exc.detail}", exc_info=True)
        return StreamingResponse(
            iter([f"data: ERROR: {http_exc.detail}\n\n".encode("utf-8")]),
            media_type="text/event-stream",
            status_code=http_exc.status_code,
        )
    except (ChatServiceError, OpenAIError, Exception) as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", str(e))
        logging.error(f"Error processing request: {detail}", exc_info=True)
        return StreamingResponse(
            iter(
                [
                    f"data: ERROR: An unexpected server error occurred: {detail}\n\n".encode(
                        "utf-8"
                    )
                ]
            ),
            media_type="text/event-stream",
            status_code=status_code,
        )


@app.cosmos_db_input(
    arg_name="documents",
    database_name=app_config.COSMOS_DATABASE_NAME,
    container_name=app_config.COSMOS_CONTAINER_NAME,
    connection="CosmosDBConnection",
    sql_query="SELECT c.id, c.title FROM c",
)
@app.route(route="fetch_chats", auth_level=func.AuthLevel.FUNCTION)
async def get_all_metadata_ids(req: Request, documents: func.DocumentList) -> Response:
    logging.info("Python HTTP trigger function processed a request for fetch_chats.")
    try:
        if not documents:
            logging.warning("No documents found in the specified Cosmos DB container.")
            logging.info("Creating new chat!")
            cosmos_history = await chat_history_service.create_new_chat_history()
            documents.append(
                {"id": cosmos_history.session_id, "title": cosmos_history.title}
            )

        metadata_ids = [
            {"id": doc.get("id"), "title": doc.get("title")}
            for doc in documents
            if doc.get("id")
        ]

        logging.info(f"Successfully fetched {len(metadata_ids)} metadata IDs.")
        return Response(
            content=json.dumps(metadata_ids),
            media_type="application/json",
            status_code=200,
        )
    except Exception as e:
        logging.error(f"An error occurred in fetch_chats: {e}", exc_info=True)
        return Response(
            content=json.dumps({"error": f"An error occurred: {str(e)}"}),
            status_code=500,
            media_type="application/json",
        )


@app.route(route="create_chat", methods=[func.HttpMethod.POST])
async def create_new_chat(req: Request) -> Response:
    logging.info("Received request for /create_chat")
    try:
        cosmos_history = await chat_history_service.create_new_chat_history()
        chat_info = json.dumps(
            {"id": cosmos_history.session_id, "title": cosmos_history.title}
        )
        return Response(chat_info, status_code=200, media_type="application/json")
    except ChatServiceError as e:
        logging.error(f"Error creating new chat: {e.detail}", exc_info=True)
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        logging.error(f"Unexpected error creating new chat: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected server error occurred: {e}"},
        )


@app.route(route="fetch_chat", methods=[func.HttpMethod.GET])
async def fetch_chat(req: Request) -> Response:
    """
    Accepts a chatId and returns list of messages associated with it, if exists.
    """
    logging.info("Received request for /fetch_chat")
    chat_id = req.query_params.get("chat_id")

    if not chat_id:
        return JSONResponse(
            {"error": "ChatID is a required attribute"},
            status_code=400,
        )

    try:
        history = await chat_history_service.get_history_instance(chat_id)
        messages = await history.aget_messages()
        files = history._load_existing_files()

        message_list = []
        for message in messages:
            role = None
            if message.type == "ai":
                role = "agent"
            elif message.type == "human":
                role = "user"
            if role:
                message_list.append({"role": role, "value": message.content})

        return JSONResponse(
            content={"messages": message_list, "files": files},
            status_code=200,
        )
    except ChatServiceError as e:
        logging.error(f"Error fetching chat {chat_id}: {e.detail}", exc_info=True)
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        logging.error(f"Unexpected error fetching chat {chat_id}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected server error occurred: {e}"},
        )


@app.route("delete_chat/{chat_id}", methods=[func.HttpMethod.DELETE])
@app.cosmos_db_input(
    arg_name="documents",
    database_name=app_config.COSMOS_VECTOR_DB_NAME,
    container_name=app_config.COSMOS_VECTOR_CONTAINER_NAME,
    connection="CosmosDBConnection",
    sql_query="SELECT c.id FROM c WHERE c.metadata.chat_id = {chat_id}",
)
async def delete_chat(req: Request, documents: func.DocumentList) -> Response:
    logging.info(f"Received request for /delete_chat/{req.path_params.get('chat_id')}")
    chat_id = req.path_params.get("chat_id")
    if not chat_id:
        return JSONResponse(
            {"error": "chat_id is a required path parameter"},
            status_code=400,
        )

    try:
        await chat_history_service.clear_chat_history(chat_id)

        if documents:
            doc_ids_to_delete = [doc.get("id") for doc in documents if doc.get("id")]
            vector_store_service.delete_documents_by_id(doc_ids_to_delete)
        else:
            logging.info(f"No vector documents found to delete for chat ID: {chat_id}")

        return JSONResponse(
            content={"message": "Chat and associated documents deleted successfully!"},
            status_code=200,
        )
    except ChatServiceError as e:
        logging.error(f"Error deleting chat {chat_id}: {e.detail}", exc_info=True)
        return JSONResponse(status_code=e.status_code, content={"error": e.detail})
    except Exception as e:
        logging.error(f"Unexpected error deleting chat {chat_id}: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected server error occurred: {e}"},
        )


@app.route(route="upload", methods=[func.HttpMethod.POST])
async def upload(req: Request) -> JSONResponse:
    logging.info("Received request for /upload")
    temp_file_path = None
    try:
        form_data = await req.form()
        chat_id: str = form_data.get("chatId")
        uploaded_file: UploadFile = form_data.get("file")

        if not chat_id:
            return JSONResponse(
                {"error": "Form field 'chatId' is required."},
                status_code=400,
            )

        temp_file_path = await file_handler.save_uploaded_file_temporarily(
            uploaded_file
        )

        documents = file_handler.process_pdf_documents(
            temp_file_path, chat_id, uploaded_file.filename
        )
        await vector_store_service.add_documents_to_vector_store(documents)

        history = await chat_history_service.get_history_instance(session_id=chat_id)
        current_files = history._load_existing_files()
        updated_files = list(set(current_files + [uploaded_file.filename]))
        history.set_files(updated_files)

        logging.info(
            f"Updated chat {chat_id} history with new file: {uploaded_file.filename}"
        )

        response_data = {
            "message": "File processed and indexed successfully!",
            "original_file_name": uploaded_file.filename,
            "content_type": uploaded_file.content_type,
            "file_size_bytes": os.path.getsize(temp_file_path),
        }
        return JSONResponse(content=response_data, status_code=200)

    except (HTTPException, FileProcessingError, ChatServiceError) as http_exc:
        logging.error(f"HTTP Error during upload: {http_exc.detail}", exc_info=True)
        return JSONResponse(
            status_code=http_exc.status_code, content={"error": http_exc.detail}
        )
    except Exception as e:
        logging.exception(
            "An unexpected error occurred during file upload and processing."
        )
        return JSONResponse(
            status_code=500,
            content={"error": f"An unexpected server error occurred: {e}"},
        )
    finally:
        file_handler.cleanup_temporary_file(temp_file_path)
