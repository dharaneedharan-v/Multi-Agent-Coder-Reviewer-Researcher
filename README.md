# Multi-Agent Coder · Reviewer · Researcher

A **LangGraph-orchestrated multi-agent system** that routes a developer's natural-language request to one of three specialist AI agents — **Coder**, **Reviewer**, and **Researcher** — and returns a final, review-passed answer. Built as a FastAPI backend (`MCP_Client`) paired with a dedicated tool server (`MCP_Server`) exposed over the **Model Context Protocol (MCP)**.

> Ask it to write code, review code, research a technology, or do both research + code in one turn — an LLM-based router decides which specialist(s) handle your request, and a reviewer loop keeps sending failed code back for fixes until it passes (or hits a retry limit).

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [How a Request Flows](#how-a-request-flows)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [API Reference](#api-reference)
- [MCP Server Tools](#mcp-server-tools)
- [Conversation Memory](#conversation-memory)
- [Known Issues](#known-issues)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview

This project is a two-service system:

| Service | Role |
|---|---|
| **`MCP_Client`** | FastAPI app exposing a `/chat` endpoint. Contains the LangGraph state machine, the three agents (Coder, Researcher, Reviewer), an intent router, Postgres-backed conversation checkpointing, and error logging. |
| **`MCP_Server`** | A `FastMCP` tool server that exposes reusable tools — `format_python`, `lint_python`, and `duckduckgo_search` — over the MCP protocol, consumed by the agents in `MCP_Client`. |

Every incoming chat message is classified by an LLM router into one of five intents, and the LangGraph graph routes execution accordingly — including a **self-correcting review loop** where failing code is sent back to the researcher/coder nodes with the reviewer's feedback until it passes or a retry cap is reached.

---

## Architecture

```
                          ┌─────────────┐
                          │   /chat     │  FastAPI (MCP_Client)
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │   router    │  LLM intent classifier
                          │   (node)    │  → code / review / research /
                          └──────┬──────┘    research_and_code / irrelevant
                 ┌───────────────┼────────────────┐
                 │               │                │
          ┌──────▼─────┐  ┌──────▼──────┐  ┌──────▼──────┐
          │ researcher │─▶│    coder    │─▶│  reviewer   │
          │  (node)    │  │   (node)    │  │   (node)    │
          └────────────┘  └─────────────┘  └──────┬──────┘
                 ▲                                 │
                 │            FAIL (retry < 3)      │
                 └─────────────────────────────────┘
                                 │ PASS / max retries
                                 ▼
                              END → final_response
```

- **Router node** — a lightweight LLM call (`max_tokens=50`) classifies the user's message into an `Intent` enum (`code`, `review`, `research`, `research_and_code`, `irrelavent`) and dispatches to the right node.
- **Researcher node** — a ReAct agent (`langgraph.prebuilt.create_react_agent`) with access to the MCP `duckduckgo_search` tool. Produces technical research/context, either as the final answer (pure research) or as input to the coder (research_and_code / retry loop).
- **Coder node** — a ReAct agent that writes/fixes code, optionally guided by research context and prior reviewer issues.
- **Reviewer node** — a ReAct agent with access to MCP `format_python` / `lint_python` tools. Reviews either user-submitted code or coder-generated code, returns a `PASS`/`FAIL` verdict plus issues, and drives the retry loop (capped at `MAX_REVIEW_RETRIES = 3`).

All conversation state (`GraphState`) — messages, intent, research context, review feedback/issues, retry count, final response — flows through the graph and is checkpointed per customer using `AsyncPostgresSaver`, so multi-turn conversations resume correctly.

---

## How a Request Flows

1. Client calls `POST /chat` with `{ "message": "...", "customer_id": ... }`.
2. `AgentService` looks up the customer, opens a Postgres-backed LangGraph checkpointer keyed on `thread_id = customer_id`, and determines if this is the first turn.
3. The graph runs starting at the **router** node:
   - `code` → straight to **coder** → `END`
   - `review` → **reviewer** (reviews user-supplied code) → loops to researcher/coder on `FAIL`
   - `research` → **researcher** → `END`
   - `research_and_code` → **researcher** → **coder** → **reviewer** → loop until `PASS` or retry cap
   - `irrelavent` → `END` with a canned "outside my technical scope" response
4. The reviewer loop retries up to `MAX_REVIEW_RETRIES` (3) times, sending issues back through the researcher before returning to the coder.
5. `final_response` is returned to the client as part of a standardized `APIResponse` envelope.

---

## Project Structure

```
Multi-Agent-Coder-Reviewer-Researcher/
├── MCP_Client/                       # FastAPI app: agents, graph, API
│   ├── main.py                       # App entrypoint, DB init, migrations, uvicorn server
│   ├── requiements.py                # Dependency list (see note in Setup)
│   ├── pyproject.toml
│   ├── env.txt                       # Sample env vars (rename to .env — see Known Issues)
│   └── src/
│       ├── settings.py               # dataclass Config loaded from environment
│       ├── agent/
│       │   ├── coder_agent.py        # Coder ReAct agent (+ optional Context7 MCP tools)
│       │   ├── research_agent.py     # Researcher ReAct agent (MCP: duckduckgo_search)
│       │   └── review_agent.py       # Reviewer ReAct agent (MCP: format/lint) + verdict parsing
│       ├── prompt/
│       │   ├── coder_prompt.py       # Senior-engineer system prompt
│       │   ├── research_prompt.py    # "Head of R&D" system prompt
│       │   ├── review_prompt.py      # "Master Roaster" reviewer system prompt
│       │   └── router_prompt.py      # Intent enum + router system prompt
│       ├── service/
│       │   ├── graph.py              # LangGraph StateGraph: nodes, routing, retry loop
│       │   └── agentservice.py       # Orchestrates checkpointer + graph.ainvoke per chat turn
│       ├── models/
│       │   └── models.py             # Pydantic/TypedDict: APIResponse, ChatRequest, GraphState
│       ├── routes/
│       │   └── routes.py             # POST /chat
│       ├── repositories/
│       │   ├── database.py           # Singleton SQLAlchemy engine/session (Postgres)
│       │   ├── repository.py         # CoffeeRepository: customer lookup, error logging
│       │   └── schema/schema.py      # ORM models: Customer, Error
│       ├── migrations/
│       │   ├── create_tables.py      # Creates tables if not present
│       │   ├── seeder.py             # Seeds sample customers + error logs
│       │   └── factory/factory.py    # Faker-based factories (Customer/Product/Order)
│       └── utils/
│           ├── LLM/invoke.py         # ChatBedrock (AWS Bedrock) LLM + DB URI factory
│           ├── exceptions/           # AppException, error codes, global FastAPI handlers
│           ├── logger/log.py         # Colorized logging + DB-backed error logging
│           └── helpers.py            # success_response / error_response helpers
│
├── MCP_Server/                       # FastMCP tool server
│   ├── main.py                       # FastMCP app ("router") mounting tools
│   ├── pyproject.toml
│   └── src/
│       ├── tools/tools.py            # @router.tool(): format_python, lint_python, duckduckgo_search
│       ├── repositories/             # Same Database/Repository/Schema pattern as MCP_Client
│       └── utils/
│           ├── helper.py
│           └── logger/log.py
│
└── .gitignore
```

---

## Tech Stack

- **Orchestration:** [LangGraph](https://github.com/langchain-ai/langgraph) (`StateGraph`, conditional edges, `AsyncPostgresSaver` checkpointing)
- **Agents:** [LangChain](https://github.com/langchain-ai/langchain) `create_react_agent`, `langchain_mcp_adapters` (MultiServerMCPClient)
- **LLM:** AWS Bedrock via `langchain_aws.ChatBedrock` (model configured via `MODEL_ID`)
- **Tool Server:** [FastMCP](https://github.com/jlowin/fastmcp) — exposes tools over `streamable_http`
- **API:** FastAPI + Uvicorn
- **Database:** PostgreSQL via SQLAlchemy (ORM) + `asyncpg`/`psycopg` (checkpointing + app data)
- **Code Quality Tools (server-side):** `black` (formatting), `ruff` (linting)
- **Web Search:** `duckduckgo_search` (DDGS)
- **Data Generation:** `Faker`, `boto3` (AWS)
- **Package/Env Management:** [`uv`](https://github.com/astral-sh/uv)
- **Python:** 3.13

---

## Prerequisites

- Python **3.13**
- [`uv`](https://docs.astral.sh/uv/) installed
- A running **PostgreSQL** instance
- AWS credentials with **Bedrock** access (for the LLM) and, optionally, **Bedrock Data Automation** access (ARNs referenced in config)
- (Optional) A [Context7](https://context7.com/) API key if you enable the Context7 MCP tools in the coder agent

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/dharaneedharan-v/Multi-Agent-Coder-Reviewer-Researcher.git
cd Multi-Agent-Coder-Reviewer-Researcher
```

### 2. Configure environment variables

Each service (`MCP_Client`, `MCP_Server`) loads its own environment via `python-dotenv`. Create a `.env` file in **each** service directory (`MCP_Client/.env` and `MCP_Server/.env`) — see [Environment Variables](#environment-variables) below for the full list. `MCP_Client/env.txt` shows the expected keys/shape, but **do not commit real secrets in a plain, tracked file** — copy its contents into a local `.env` (already covered by `.gitignore`) instead.

### 3. Install dependencies

Dependencies are currently listed as pip-style requirements inside `MCP_Client/requiements.py` and `MCP_Server/pyproject.toml`. Until they're consolidated, install with:

```bash
# From MCP_Client/
uv venv
uv pip install fastapi uvicorn boto3 faker pgvector asyncpg \
  "sqlalchemy[asyncio]" "psycopg[binary]" "pydantic[email]" \
  python-dotenv pyyaml langchain langchain_aws \
  langgraph-checkpoint-postgres langchain_mcp_adapters langgraph

# From MCP_Server/
uv venv
uv pip install fastmcp langchain-core duckduckgo-search black ruff sqlalchemy "psycopg[binary]" python-dotenv
```

> Tip: rename `MCP_Client/requiements.py` to a standard `requirements.txt` (or a proper `pyproject.toml` dependency list) so `uv pip install -r requirements.txt` / `uv sync` works out of the box.

### 4. Database

The app creates its own tables and seeds sample data on startup (see `main.py` → `run_local_server()`), as long as `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USERNAME`/`DB_PASSWORD` point at a reachable Postgres instance and the target database already exists.

---

## Environment Variables

Set these in `MCP_Client/.env` (values shown are illustrative — replace with your own):

| Variable | Description |
|---|---|
| `DB_HOST` | Postgres host (e.g. `localhost`) |
| `DB_PORT` | Postgres port (e.g. `5432`) |
| `DB_NAME` | Database name |
| `DB_USERNAME` | Database user |
| `DB_PASSWORD` | Database password |
| `PORT` | Port the FastAPI app listens on (default `8080`) |
| `HOST` | Bind host (default `127.0.0.1`) |
| `LOG_LEVEL` | Logging level (default `INFO`) |
| `MODEL_ID` | Bedrock model / inference profile ARN used by `ChatBedrock` |
| `REGION` | AWS region for Bedrock (default `us-east-1`) |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | AWS credentials for Bedrock |
| `PROJECT_ARN` / `PROFILE_ARN` | AWS Bedrock Data Automation project/profile ARNs |
| `INPUT_S3_URI` / `OUTPUT_S3_URI` | S3 input/output locations for Bedrock Data Automation |
| `BLUEPRINT_NAME` | Bedrock Data Automation blueprint name |
| `S3_BUCKET` | S3 bucket used for the above |
| `CONTEXT7_API_KEY` | API key for the optional Context7 MCP tool (coder agent) |
| `MCP_SERVER_URL` / `PEP8_MCP_URL` | URL(s) of the running `MCP_Server` instance |

`MCP_Server/.env` only needs the `DB_*` variables (it shares the same `Database`/`settings` pattern).

**Security note:** rotate any key that has previously been committed to source control (see [Known Issues](#known-issues)), and keep `.env` out of git — only commit an `.env.example` with placeholder values.

---

## Running the Project

Start the **MCP tool server** first, then the **client API**.

```bash
# Terminal 1 — MCP_Server (tool server: format/lint/search)
cd MCP_Server
uv run main.py

# Terminal 2 — MCP_Client (FastAPI app: chat API + agents)
cd MCP_Client
uv run main.py
```

By default the client serves on `http://127.0.0.1:8080` (configurable via `HOST`/`PORT`). Confirm `MCP_SERVER_URL` (and the URLs hardcoded in `research_agent.py` / `review_agent.py`) point at wherever `MCP_Server` is actually listening — see [Known Issues](#known-issues).

---

## API Reference

### `POST /chat`

**Request body**

```json
{
  "message": "Write a Python function to check if a number is prime",
  "customer_id": 1
}
```

**Response**

```json
{
  "code": 200,
  "status": "success",
  "message": "Chat processed successfully",
  "data": "def is_prime(n: int) -> bool:\n    ...",
  "error": null,
  "request_id": "8e2f5f2a-...",
  "timestamp": "2026-09-03T12:00:00+00:00"
}
```

`customer_id` doubles as the LangGraph checkpoint `thread_id`, so conversations persist per customer across turns.

---

## MCP Server Tools

Exposed by `MCP_Server` over `streamable_http` and consumed by the agents via `langchain_mcp_adapters`:

| Tool | Used By | Description |
|---|---|---|
| `format_python(code)` | Reviewer agent | Formats Python code with `black` and returns the formatted result. |
| `lint_python(code)` | Reviewer agent | Lints Python code with `ruff check` and returns output + an error flag. |
| `duckduckgo_search(query, max_results=5)` | Researcher agent | Searches the web via DuckDuckGo and returns formatted title/URL/snippet results. |

The coder agent also has an (currently commented-out) integration point for the external [Context7](https://context7.com/) MCP server for up-to-date library documentation.

---

## Conversation Memory

Multi-turn context is preserved with `langgraph.checkpoint.postgres.aio.AsyncPostgresSaver`, keyed by `thread_id = customer_id`. On each turn, `AgentService` checks whether a prior checkpoint exists to determine `is_first_turn`, then re-invokes the graph with the same thread, so state like retry counts and prior context is available across the review loop and across separate `/chat` calls.

---

## Known Issues

These were found while reading the code and should be fixed before relying on this in a fresh environment:

- **Broken import — coder prompt:** `agent/coder_agent.py` imports from `src.prompt.code_prompt`, but the actual module is `src/prompt/coder_prompt.py`.
- **Case-sensitive `Database` import:** `main.py`, `migrations/create_tables.py`, and `migrations/seeder.py` import `src.repositories.Database`, but the file is `database.py` (lowercase). This works on case-insensitive filesystems (macOS/Windows) but fails on Linux/most CI.
- **Broken import — error codes:** `utils/exceptions/error.py` imports `src.utils.exceptions.error_codes`, but the file is `error_code.py` (singular).
- **Missing module:** `agent/research_agent.py` imports `duckduckgo_search` from `src.tools.duck`, which doesn't exist in `MCP_Client`. The real `duckduckgo_search` implementation lives server-side, in `MCP_Server/src/tools/tools.py`, and is meant to be consumed as an MCP tool, not imported directly.
- **Inconsistent MCP server URLs:** `research_agent.py` points to `http://127.0.0.1:8000/mcp`, while `review_agent.py` points to `http://127.0.0.1:8002/mcp`. `MCP_Server` is a single service — confirm which port it should actually run on and align both agents (and `MCP_SERVER_URL`/`PEP8_MCP_URL` in `.env`).
- **`MCP_Server/main.py` never starts the server:** the `router.run(transport="streamable-http", port=8002)` call is commented out, so running `uv run main.py` in `MCP_Server` currently does nothing.
- **Secret committed to the repo:** `MCP_Client/env.txt` contains a real-looking `CONTEXT7_API_KEY`. Rotate it and remove it from git history; use an untracked `.env` instead.
- **Dependency list is a `.py` file:** `MCP_Client/requiements.py` (note the typo) is pip-style text disguised as a Python module — convert it to `requirements.txt` or move dependencies into `pyproject.toml` so `uv sync` works.

---

## Roadmap

- [ ] Fix the import/path mismatches listed above
- [ ] Consolidate dependency declarations into `pyproject.toml` for both services
- [ ] Align MCP server ports/URLs between `MCP_Server` and both consuming agents
- [ ] Add automated tests for the router's intent classification and the review retry loop
- [ ] Add a `docker-compose.yml` for Postgres + both services
- [ ] Wire up the Context7 MCP integration in the coder agent (currently commented out)

---
