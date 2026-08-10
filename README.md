# Enterprise AI Knowledge Assistant

A full-stack enterprise knowledge assistant that lets users upload internal documents and ask questions about their content.

The application combines Retrieval-Augmented Generation, LangGraph-based agentic orchestration, OpenAI models, ChromaDB vector search, conversation memory, source attribution, streaming responses, evaluation, and observability.

The main goal is simple: give users useful answers from their own documents while avoiding unsupported answers when relevant information cannot be found.

## What the application does

The application supports two main workflows.

### 1. Document ingestion

Users can upload supported business documents. The backend validates the file, stores it locally, checks for duplicate content, reads the document, breaks the content into smaller chunks, and indexes those chunks in ChromaDB.

Supported file formats:

- PDF
- TXT
- CSV
- XLSX

Once a document is indexed, its content can be searched when users ask questions.

### 2. Question answering

Users ask questions through the application. The backend runs the question through a LangGraph workflow.

The workflow decides whether document retrieval is needed, searches ChromaDB for relevant document chunks, builds a grounded prompt, asks the OpenAI language model to generate an answer, validates the result, and returns source information with the response.

If the system does not find sufficiently relevant document content, it does not send unrelated context to the language model. Instead, it returns a safe response explaining that the information could not be found in the provided documents.

## High-level architecture

```text
User
 |
 v
Next.js Frontend
 |
 | REST API / Server-Sent Events
 v
FastAPI Backend
 |
 +------------------------+-------------------------+
 |                                                  |
 | Document Management                              | Question Answering
 |                                                  |
 v                                                  v
Validation Service                              LangGraph Workflow
 |                                                  |
 v                                                  v
Storage Service                                  Planner
 |                                                  |
 v                                                  v
Duplicate Detection                      Retrieval required?
 |                                             /           \
 v                                           Yes            No
Loader Factory                                  |             |
 |                                              v             |
 v                                          Retrieval          |
Document Loader                                  |             |
 |                                              v             |
 v                                            ChromaDB         |
Chunk Service                                    |             |
 |                                              v             |
 v                                        Relevant context?    |
Embedding + Vector Store                    /           \      |
 |                                          Yes          No     |
 v                                           |            |     |
ChromaDB                                     v            v     |
                                         Reasoning   Safe fallback
                                              \           /
                                               v         v
                                                Validation
                                                    |
                                                    v
                                         Answer + Sources
                                                    |
                                                    v
                                                   User
```

## Technology stack

| Area | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript |
| UI | Tailwind CSS 4, shadcn, Base UI |
| Frontend animation | Framer Motion |
| Backend API | FastAPI |
| Agent orchestration | LangGraph |
| LLM integration | OpenAI through LangChain |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector database | ChromaDB |
| RAG framework | LangChain components with custom services |
| Conversation state | In-memory conversation memory |
| Evaluation | LangSmith datasets and evaluators |
| Observability | Application logging and LangSmith tracing |
| Document metadata | Local document repository |
| File storage | Local filesystem |
| Testing | pytest |
| Container support | Docker |

## Repository structure

```text
enterprise-ai-knowledge-assistant/
|
+-- backend/
|   +-- app/
|   |   +-- ai/
|   |   |   +-- agentic/
|   |   |   +-- chunking/
|   |   |   +-- embeddings/
|   |   |   +-- evaluation/
|   |   |   +-- indexing/
|   |   |   +-- llm/
|   |   |   +-- loaders/
|   |   |   +-- memory/
|   |   |   +-- models/
|   |   |   +-- retrieval/
|   |   |   +-- vectorstores/
|   |   +-- api/
|   |   +-- core/
|   |   +-- data/
|   |   +-- repositories/
|   |   +-- schemas/
|   |   +-- scripts/
|   |   +-- services/
|   |   +-- dependencies.py
|   |   +-- main.py
|   +-- tests/
|   +-- Dockerfile
|   +-- Makefile
|   +-- requirements.txt
|
+-- frontend/
|   +-- app/
|   +-- components/
|   +-- hooks/
|   +-- public/
|   +-- services/
|   +-- types/
|   +-- utils/
|   +-- package.json
|
+-- docs/
+-- infrastructure/
+-- scripts/
+-- docker-compose.yml
+-- LICENSE
+-- README.md
```

## Document ingestion flow

The ingestion pipeline prepares uploaded documents for later semantic search.

### Step 1: Upload

A client sends a document to:

```text
POST /api/v1/upload
```

The FastAPI route passes the uploaded file to `DocumentService`.

### Step 2: Validate

`ValidationService` checks the uploaded file before it is accepted.

The current configuration allows PDF, TXT, CSV, and XLSX files, with a default maximum upload size of 25 MB.

### Step 3: Store

`StorageService` saves the accepted file in the configured upload directory.

The storage layer assigns a document identifier and keeps the original filename as metadata.

### Step 4: Detect duplicates

`DocumentService` calculates a SHA-256 hash of the stored file.

The hash is checked against the document repository. If the same content has already been uploaded, the newly stored copy is removed and the upload is rejected as a duplicate.

### Step 5: Select a loader

`LoaderFactory` selects a loader based on the file extension.

```text
.pdf  -> PdfLoader
.txt  -> TxtLoader
.csv  -> CsvLoader
.xlsx -> ExcelLoader
```

### Step 6: Load and enrich content

The selected loader converts the document into LangChain `Document` objects.

Storage metadata such as `document_id`, original filename, and stored filename is added before chunking.

### Step 7: Chunk the document

`ChunkService` divides the loaded content into smaller pieces.

The default configuration uses:

```text
Chunk size:    1000
Chunk overlap: 200
```

Chunking allows the retrieval system to find the most relevant parts of a large document instead of passing the entire file to the language model.

### Step 8: Create embeddings and index

The document chunks are added to the vector store.

The project uses ChromaDB as the vector database and OpenAI embeddings. The default embedding model is:

```text
text-embedding-3-small
```

After indexing is complete, the document is registered with metadata including upload time, content type, size, chunk count, and indexing status.

## Agentic question-answering flow

The question-answering workflow is implemented with LangGraph.

The graph uses shared `GraphState` so each node can add information to the same request state.

Important state includes:

```text
question
request_id
intent
retrieval_strategy
top_k
requires_retrieval
retrieved_chunks
prompt
answer
validated
confidence_score
sources
metadata
conversation_history
```

### Planner

The Planner is the first node.

Its job is to understand the request and decide how the workflow should proceed.

It can determine:

- request intent
- retrieval strategy
- number of results to retrieve
- whether document retrieval is required

After planning, LangGraph conditionally routes the request.

```text
START
  |
  v
Planner
  |
  +---- retrieval required ----> Retrieval
  |
  +---- retrieval not required -> Reasoning
```

### Retrieval

When retrieval is required, `RetrievalService` searches ChromaDB for semantically similar document chunks.

The current default settings include:

```text
Default top_k:              5
Similarity score threshold: 0.15
```

Retrieved chunks below the configured threshold are removed.

This reduces the chance of passing unrelated document content to the language model.

### No-context protection

After retrieval, the graph checks whether relevant content was found.

If relevant content exists:

```text
Retrieval -> Reasoning
```

If no relevant content exists:

```text
Retrieval -> No Context -> Validation
```

The no-context node skips LLM reasoning and returns:

```text
I couldn't find that information in the provided documents.
```

This is an important guardrail because it reduces unsupported answers when the knowledge base does not contain useful evidence.

### Reasoning

The Reasoning node uses the retrieved context, user question, and conversation history to build the final prompt.

`PromptBuilder` prepares the prompt and `LLMService` sends it to the configured OpenAI chat model.

The default configured chat model is:

```text
gpt-5
```

The generated response is stored in the graph state.

### Validation and source attribution

The Validation node runs after reasoning or after the no-context path.

It prepares source information from the retrieved documents and adds it to the response state.

This allows the API to return both the answer and the documents used to support that answer.

### Final LangGraph flow

```text
START
  |
  v
Planner
  |
  +-----------------------+
  |                       |
  | retrieval             | no retrieval
  v                       |
Retrieval                  |
  |                        |
  v                        |
Relevant context?          |
  |                        |
  +-- Yes --> Reasoning <--+
  |
  +-- No --> No Context
                |
                v
             Validation
                |
                v
               END
```

## Conversation memory

The workflow accepts a `session_id` with each chat request.

Conversation history is loaded before processing the current question and is passed through `GraphState`.

The user message is stored before workflow execution, and the assistant answer is stored after successful completion.

This allows follow-up questions to use previous conversation context within the same application session.

The current implementation uses application-level conversation memory rather than an external persistent conversation database.

## Streaming responses

The backend supports both normal and streaming chat APIs.

Standard request:

```text
POST /api/v1/chat
```

Streaming request:

```text
POST /api/v1/chat/stream
```

The streaming endpoint uses Server-Sent Events.

During execution, the workflow can stream LLM tokens and LangGraph updates. The endpoint sends a final `done` event when processing completes.

This gives the frontend a better chat experience because users can see the response while it is being generated.

## Document management

The project also exposes APIs for document management.

### List documents

```text
GET /api/v1/documents
```

Returns registered documents and metadata such as filename, content type, size, upload time, chunk count, and indexing status.

### Delete a document

```text
DELETE /api/v1/documents/{document_id}
```

Deletion removes:

1. ChromaDB chunks associated with the document
2. The physical uploaded file
3. The document metadata record

This prevents deleted documents from continuing to appear in future retrieval results.

## API summary

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/upload` | Upload and index a document |
| GET | `/api/v1/documents` | List indexed documents |
| DELETE | `/api/v1/documents/{document_id}` | Delete a document and its indexed data |
| POST | `/api/v1/chat` | Ask a question and receive a complete response |
| POST | `/api/v1/chat/stream` | Ask a question and receive an SSE streaming response |
| GET | `/api/v1/health` | Application health check |

FastAPI also provides interactive API documentation when the backend is running:

```text
http://localhost:8000/docs
```

## Observability

The backend records operational information such as:

- request identifier
- session identifier
- workflow duration
- node execution information
- retrieval scores
- document source and page
- workflow success or failure
- indexing activity

Each workflow execution receives a unique `request_id`.

The project also supports LangSmith tracing through configuration variables.

```text
LANGSMITH_TRACING
LANGSMITH_API_KEY
LANGSMITH_PROJECT
```

LangSmith makes it possible to inspect LLM and LangGraph execution outside normal application logs.

## AI evaluation

The project contains an evaluation module under:

```text
backend/app/ai/evaluation/
```

The evaluation runner executes test questions through the same production `AgenticWorkflow` used by the API.

The current evaluation checks three areas:

### Answer correctness

An LLM judge compares the generated answer with a reference answer and returns a correctness score.

### Source match

The evaluator checks whether the expected source appears in the returned source list.

### Unanswerable behavior

Questions marked as unanswerable are checked to make sure the assistant safely indicates that enough information is not available.

Evaluation experiments are sent to LangSmith using the dataset:

```text
enterprise-ai-rag-evaluation
```

This provides a repeatable way to measure changes to retrieval, prompts, models, and workflow logic.

## Configuration

Backend configuration is managed through environment variables using Pydantic Settings.

Create an environment file inside the `backend` directory.

```bash
cd backend
cp .env.example .env
```

A typical local configuration can include:

```env
APP_NAME=Enterprise AI Knowledge System
APP_VERSION=0.1.0
ENVIRONMENT=development

HOST=0.0.0.0
PORT=8000

OPENAI_API_KEY=your_openai_api_key
CHAT_MODEL=gpt-5
EMBEDDING_MODEL=text-embedding-3-small

UPLOAD_DIR=app/uploads
CHROMA_DB_DIR=app/chroma_db

MAX_UPLOAD_SIZE_MB=25
LOG_LEVEL=INFO

LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=enterprise-ai-knowledge-assistant
```

Do not commit real API keys.

## Running the backend locally

### Requirements

- Python 3.11 or compatible project version
- OpenAI API key

Create and activate a virtual environment.

```bash
cd backend

python -m venv .venv
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create `.env` from the example file and add your OpenAI API key.

Run FastAPI:

```bash
uvicorn app.main:app --reload --env-file .env
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## Running the frontend locally

### Requirements

- Node.js
- npm

Install dependencies:

```bash
cd frontend
npm install
```

Start the development server:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

The FastAPI backend currently allows local frontend requests from `http://localhost:3000`.

## Running tests

From the backend directory:

```bash
pytest
```

The repository contains tests for API behavior and AI workflow components.

Tests should be run after changes to retrieval, prompting, graph routing, validation, indexing, or service logic.

## Running the LangSmith evaluation

Make sure the required LangSmith and OpenAI environment variables are configured.

From the backend directory:

```bash
python -m app.ai.evaluation.runner
```

The runner executes the evaluation dataset against the production agentic workflow and sends the results to LangSmith.

## Design choices

### Why LangGraph?

The question-answering pipeline is more than a single prompt.

The application needs to plan, retrieve information, decide what to do when nothing useful is found, reason over context, validate the result, and preserve workflow metadata.

LangGraph makes those steps explicit and allows conditional routing between them.

### Why ChromaDB?

ChromaDB provides local vector storage that works well for development and experimentation.

The application wraps vector operations behind `VectorStoreService`, which keeps the higher-level retrieval code less dependent on the specific vector database implementation.

### Why a retrieval threshold?

A vector search will usually return something even when the returned chunks are weak matches.

The similarity threshold filters weak results before reasoning.

If nothing passes the threshold, the system uses its safe no-context flow rather than asking the model to generate an answer from unrelated content.

### Why source attribution?

A useful enterprise assistant should make it possible to understand where an answer came from.

The validation stage attaches source metadata so consumers of the API can show supporting document information next to generated answers.

### Why duplicate detection?

Uploading the same document multiple times would create duplicate vector chunks and could distort retrieval results.

The application calculates a SHA-256 content hash during upload and rejects content that already exists in the document registry.

## Current implementation notes

This project is designed as a production-oriented learning and reference implementation, but some components are intentionally local.

Current local components include:

- filesystem document storage
- ChromaDB persistence
- application-level conversation memory
- local document metadata storage

For a larger production deployment, these boundaries can be replaced with managed services without changing the overall application flow.

Examples include object storage for uploaded files, a managed vector database, persistent conversation storage, centralized application telemetry, authentication, authorization, and cloud deployment.

## Future Enhancements

The current version focuses on demonstrating the complete Enterprise AI and RAG workflow locally. The architecture is designed so that local components can later be replaced with managed cloud services.

### AWS Deployment

Deploy the application to AWS to provide a scalable and production-ready runtime environment.

The frontend and backend can be containerized and deployed using AWS services such as ECS or EKS. Production deployment can also include load balancing, health checks, centralized logging, monitoring, and automated CI/CD pipelines.

### Persistent Application Storage

The current implementation uses local storage for application metadata and some runtime state.

A future version can replace local persistence with Amazon DynamoDB or another managed database service. This can store information such as:

* document metadata
* document processing status
* conversation sessions
* conversation history
* user information
* application configuration and audit information

Using persistent storage will allow application data to survive container restarts and support multiple backend instances.

Uploaded documents can also be moved from the local filesystem to Amazon S3.

### Authentication and Role-Based Access

Add authentication so users must sign in before accessing the application.

After authentication, the application can determine the user's assigned role and permissions. Authorization rules can then control which functionality and documents each user can access.

For example, roles could include:

```text
Administrator
    |
    +-- Manage users
    +-- Upload and delete documents
    +-- Access all documents
    +-- Use the knowledge assistant

Standard User
    |
    +-- Access permitted documents
    +-- Use the knowledge assistant
    +-- View permitted conversation history
```

The backend should enforce these permissions rather than relying only on frontend controls.

Document retrieval can also become role-aware so the RAG pipeline only retrieves information the authenticated user is authorized to access.

### AWS Secrets Manager

API keys and other sensitive configuration should not be stored directly in source code, committed environment files, or container images.

AWS Secrets Manager can be used to securely manage credentials such as:

* OpenAI API keys
* LangSmith API keys
* database credentials
* external service credentials
* application secrets

The application can retrieve the required secrets during startup using its assigned AWS IAM role.

This removes the need to distribute production API keys through local `.env` files.

### Production Target Architecture

A future AWS deployment could evolve toward the following architecture:

```text
                         Users
                           |
                           v
                    Authentication
                           |
                    Role / Permission
                           |
                           v
                    Next.js Frontend
                           |
                           v
                       AWS ALB
                           |
                           v
                  FastAPI Containers
                    ECS / EKS
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      DynamoDB            S3            ChromaDB /
    Application        Documents       Managed Vector
       Data                               Store
          |
          +----------------+
                           |
                           v
                    LangGraph Workflow
                           |
                    +------+------+
                    |             |
                    v             v
                  OpenAI       LangSmith
                    ^
                    |
             AWS Secrets Manager
             API Keys / Secrets
```

These enhancements would move the project from a locally running AI application toward a secure, persistent, scalable enterprise architecture.


## Architecture diagram

TODO:

## License

See the repository `LICENSE` file for licensing information.
