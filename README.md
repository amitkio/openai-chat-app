## openai-chat-app

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=white)](https://react.dev/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Azure Functions](https://img.shields.io/badge/Azure_Functions-0078D4?style=flat)](https://azure.microsoft.com/en-us/services/functions/)

<p align="center">
<img src="https://github.com/amitkio/openai-chat-app/blob/main/media/demo.gif"/>
</p>

## ✨ Features

- **Conversational AI:** Engage in natural language conversations with an Azure OpenAI-powered LLM.
- **Markdown Support:** AI responses are presented using custom Markdown components, allowing for precise control over formatting and display.
- **Document Upload:** Upload PDF and DOCX files, the contents will be automatically processed and OCRed if required (Using [unstructured](https://unstructured.io/), [PyPDF](https://github.com/py-pdf/pypdf), [tesseract-ocr](https://github.com/tesseract-ocr/tesseract)) and appended to the context of your chat.
- **Streaming Responses:** AI responses are streamed in real-time for a smooth and engaging user experience.
- **Scalable Backend:** Serverless Python Azure Functions handle API requests, including document processing, vector search, and AI interactions.

## 🚀 Technologies Used

### Frontend (React/TypeScript)

- **TypeScript:** The core language.
- **React:** Front end framework.
- **Tailwind CSS:** CSS Framework.
- **Shadcn UI:** React component library.
- **Vite:** Fast frontend build tooling.

### Backend (Python/Azure Functions)

- **Python:** The core language.
- **LangChain:** Manages LLMs, history and file processing/vectorizing.
- **Azure OpenAI Service:** Hosts the chat models and embedding models.
- **Azure Cosmos DB:** Used as the vector store for RAG documents and storing chat history.
- **Azure Functions:** Serverless framework for the backend API.

## 📋 Setup and Installation

### 1. Prerequisites

- Node.js npm/yarn
- Python 3.9+
- Azure CLI or Azure PowerShell (for deploying to Azure)
- Azure Functions Core Tools (for local Azure Functions development)
- tesseract-ocr (for image content recognition)
- poppler (for pdf processing)

### 2. Configure Azure Resources

You will need the following Azure resources:

- **Azure OpenAI Service:**
  - **Embeddings model** (e.g., `text-embedding-ada-002`).
  - **Chat model** (e.g., `gpt-35-turbo`, `gpt-4`).
- **Azure Cosmos DB (NoSQL API):**

### 3. Environment Setup

- #### Backend
  - Install Dependencies: `pip install -r requirements.txt`
  - Create `.env` file according to config.py
  - Run Azure Functions Locally: `func start`
  - Backend is now running on `localhost:7071`, this can be changed in host.json
- #### Frontend
  - Install Dependencies `npm install`
  - Start server using `npm run dev` or build using `npm run build`
  - Frontend is now running on `localhost:5173`, this can be changed in vite config
