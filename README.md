# langchain-notebooklm

A NotebookLM-style grounded research assistant built for learning LangChain and retrieval-augmented generation (RAG) in a real app structure.

This project is a small web application that lets you add source documents, ask questions about them, and receive grounded answers based only on the active sources you loaded. It is designed as a practical learning project that combines a FastAPI backend, a browser-based client, and a LangChain agent with retrieval tools.

## Project goal

The app is meant to behave like a lightweight NotebookLM experience:

- Add sources by pasting text or uploading `.txt` / `.md` files
- Toggle which sources are active
- Ask a question in natural language
- Retrieve relevant passages from the active sources
- Generate an answer grounded in those sources
- Optionally search the web with Firecrawl and index the results as new sources
- Save helpful notes during the workflow

## Stack

- Python 3.13+
- LangChain + LangGraph
- FastAPI + Uvicorn
- OpenAI models for chat + embeddings
- Firecrawl for web search and scraping
- In-memory vector storage for retrieval

## App overview

The application is a three-panel NotebookLM-inspired workspace:

```text
┌ Sources ────┬ Chat ───────────────┬ Studio ──────┐
│ add / upload│ grounded answers    │ artifacts    │
│ select      │ with citations      │ + saved notes│
│ view / del  │                     │              │
└─────────────┴─────────────────────┴──────────────┘
```

Features currently implemented in the project:

- Sources panel: add text, upload files, view content, toggle active/inactive, delete
- Chat panel: ask grounded questions using the active sources
- Note saving: save a useful answer or summary as a note
- Web search: use Firecrawl to search and index web results into the local source store

## Project structure

```text
notebooklm-starter/
├── client/                 # static frontend (HTML/CSS/JS)
├── src/
│   ├── agents/
│   │   └── chat.py         # chat agent + tools
│   ├── api/
│   │   ├── app.py          # FastAPI application
│   │   ├── schemas.py      # API contracts
│   │   ├── services.py     # business logic
│   │   └── serve.py        # server entry point
│   ├── core/
│   │   ├── firecrawl_service.py
│   │   ├── sources.py
│   │   └── store.py
│   └── app.py              # simple app entry used for testing
├── .env.example            # example environment file
├── pyproject.toml          # project dependencies and scripts
├── README.md               # this file
├── main.py                 # basic project entry
├── test_doc.txt            # sample text file
└── uv.lock                 # lock file from uv
```

## Requirements

Before running the project, make sure you have:

- Python 3.13 or newer
- `uv` installed
- An OpenAI API key
- A Firecrawl API key if you want to use web search / scraping

## Quick start

From the project folder:

```bash
uv sync
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Then edit `.env` and add your keys:

```dotenv
OPENAI_API_KEY=your_openai_key_here
FIRECRAWL_API_KEY=your_firecrawl_key_here
NOTEBOOKLM_HOST=127.0.0.1
NOTEBOOKLM_PORT=4040
```

Start the app:

```bash
uv run notebooklm-serve
```

Open the browser at:

```text
http://127.0.0.1:4040
```

If you want to override host/port manually:

```powershell
$env:NOTEBOOKLM_HOST = "0.0.0.0"
$env:NOTEBOOKLM_PORT = "4040"
uv run notebooklm-serve
```

## How to use the app

### 1. Add sources

In the web app, you can:

- paste raw text
- upload a `.txt` or `.md` file
- turn sources on/off using the active toggle

Only active sources are used for retrieval.

### 2. Ask grounded questions

- Choose one or more active sources
- Type a question in the chat box
- The agent searches the active source store for relevant documents
- The answer is generated from retrieved context

### 3. Search the web

If `FIRECRAWL_API_KEY` is configured, the system can:

- generate search queries
- search the web via Firecrawl
- scrape relevant pages
- add the scraped content as new sources in the app

### 4. Save notes

You can save notes in the app for later reference or summarization.

## API endpoints

The backend exposes the following main endpoints:

- `GET /api/health` — health check
- `GET /api/sources` — list all sources
- `POST /api/sources` — add a source from pasted text
- `POST /api/sources/upload` — upload a text file
- `GET /api/sources/{id}` — view a source by ID
- `PATCH /api/sources/{id}` — toggle active state
- `DELETE /api/sources/{id}` — delete a source
- `POST /api/chat` — send a question to the chat agent
- `GET /api/notes` — list notes
- `POST /api/notes` — create a note
- `DELETE /api/notes/{id}` — delete a note

## Running the app in a basic way

You can also do a simple smoke test using the app module:

```bash
uv run python src/app.py
```

This is useful to confirm the project imports correctly and the source store/basic chat flow is initializing.

## Troubleshooting

### Server does not start

- Run `uv sync` successfully
- Make sure `.env` exists and contains valid keys
- Check that the port is free
- Verify your OpenAI key is valid

### No response in chat

- Ensure at least one source is active
- Confirm the OpenAI API key is set correctly
- Make sure environment variables are loaded in the current shell

### Web search fails

- Confirm `FIRECRAWL_API_KEY` is present
- Verify the key is valid
- Check that the machine has internet access

## Feature status

| Feature | Status |
|---------|--------|
| Retrieval / grounded Q&A | ✅ implemented |
| Agent + tools | ✅ implemented |
| Short-term memory | ✅ implemented |
| Source upload + active toggle | ✅ implemented |
| Firecrawl web indexing | ✅ implemented |
| Notes | ✅ implemented |
| Studio artifact generation | ⏳ planned |
| Event streaming | ⏳ planned |
| Guardrails / middleware | ⏳ planned |

## Notes

This project is intended as a learning project and a practical base for building AI apps grounded in document sources. It demonstrates core RAG patterns, tool usage, and a small web application structure without requiring a large production stack.

The current implementation is intentionally simple, but it is a strong starting point for extending the project into a more complete NotebookLM-like product.
