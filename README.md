<p align="center">
  <strong>TECH SUPPORT</strong><br>
  <em>Structured Omnichannel Platform for Helpful Intelligent Assistance</em>
</p>

<p align="center">
  A production-grade RAG framework for deploying technical customer support agents<br>
  that never hallucinate, always cite sources, and know when to ask for help.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.12+-blue?style=flat-square" alt="Python" />
  <img src="https://img.shields.io/badge/fastapi-0.115+-009688?style=flat-square" alt="FastAPI" />
  <img src="https://img.shields.io/badge/react-19-61dafb?style=flat-square" alt="React" />
  <img src="https://img.shields.io/badge/postgres-pgvector-336791?style=flat-square" alt="pgvector" />
  <img src="https://img.shields.io/badge/license-proprietary-lightgrey?style=flat-square" alt="License" />
</p>

---

## The Problem

Technical support is expensive, inconsistent, and doesn't scale. AI chatbots solve the scale problem but introduce a worse one: **hallucination**. A customer asks how to replace a dryer belt and the bot confidently invents a procedure that doesn't exist. That's not support — that's a liability.

## The Philosophy

Sophia is built on a single principle: **it is always better to say "I don't know" than to make something up.**

Every design decision flows from this. The system doesn't generate answers from its training data — it retrieves passages from *your* documentation and synthesizes answers grounded exclusively in that context. When it can't find a good answer, it says so. When it's not confident, it flags that. When the question is outside its domain, it redirects. When the situation requires a human, it escalates.

This isn't a chatbot with a knowledge base bolted on. It's a **retrieval system with a language model for synthesis** — and the distinction matters.

## What It Does

Upload your technical documentation — PDFs, markdown, web pages — and Sophia indexes it into a searchable knowledge base. Customers ask questions in natural language. The system retrieves the most relevant passages using hybrid search, re-ranks them for precision, assesses its own confidence, and generates a grounded response with source citations.

The entire pipeline is observable, auditable, and configurable per deployment.

---

## Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        UI["React SPA<br/><small>Tailwind + shadcn/ui</small>"]
        Voice["Voice Agent<br/><small>LiveKit / Twilio</small>"]
    end

    subgraph API["API Layer — FastAPI"]
        Chat["/chat/stream<br/><small>SSE streaming</small>"]
        Docs["/documents<br/><small>Upload + manage</small>"]
        FB["/feedback<br/><small>Thumbs up/down</small>"]
        Voice_EP["/voice/stream<br/><small>Sentence-buffered SSE</small>"]
    end

    subgraph Core["Core Pipeline"]
        RAG["RAG Pipeline<br/><small>Orchestration</small>"]
        Ingest["Ingestion Pipeline<br/><small>Load → Clean → Chunk → Embed → Store</small>"]
    end

    subgraph Providers["Provider Layer — Swappable via Protocol"]
        LLM["LLM<br/><small>Claude, GPT, Llama</small>"]
        EMB["Embeddings<br/><small>API or Local</small>"]
        VS["Vector Store<br/><small>pgvector, Qdrant, Pinecone</small>"]
        RR["Reranker<br/><small>Cross-encoder, Cohere</small>"]
        KW["Keyword Search<br/><small>PostgreSQL FTS</small>"]
    end

    subgraph Data["Data Layer"]
        PG["PostgreSQL<br/><small>pgvector + FTS + sessions</small>"]
        Redis["Redis<br/><small>Task queue + cache</small>"]
        LF["LangFuse<br/><small>Tracing + observability</small>"]
    end

    UI -->|SSE| Chat
    Voice -->|SSE| Voice_EP
    UI --> Docs
    UI --> FB
    Chat --> RAG
    Voice_EP --> RAG
    Docs --> Ingest
    RAG --> LLM
    RAG --> EMB
    RAG --> VS
    RAG --> RR
    RAG --> KW
    Ingest --> EMB
    Ingest --> VS
    Ingest --> KW
    LLM -.-> LF
    VS --> PG
    KW --> PG
    Ingest -.-> Redis

    classDef client fill:#e8f4fd,stroke:#2196F3,color:#1565C0
    classDef api fill:#e8f5e9,stroke:#4CAF50,color:#2E7D32
    classDef core fill:#fff3e0,stroke:#FF9800,color:#E65100
    classDef provider fill:#f3e5f5,stroke:#9C27B0,color:#6A1B9A
    classDef data fill:#fce4ec,stroke:#E91E63,color:#880E4F

    class UI,Voice client
    class Chat,Docs,FB,Voice_EP api
    class RAG,Ingest core
    class LLM,EMB,VS,RR,KW provider
    class PG,Redis,LF data
```

---

## RAG Pipeline

Every query follows the same deliberate path from question to answer. No shortcuts, no guessing.

```mermaid
flowchart LR
    Q["User Query"] --> SC["Session<br/>Context"]
    SC --> QR["Query<br/>Rewrite"]
    QR --> S1["Semantic<br/>Search"]
    QR --> S2["Keyword<br/>Search"]
    S1 --> RRF["Reciprocal Rank<br/>Fusion"]
    S2 --> RRF
    RRF --> RE["Cross-Encoder<br/>Reranking"]
    RE --> CS["Confidence<br/>Scoring"]
    CS -->|ANSWER| GEN["LLM<br/>Generation"]
    CS -->|CAVEAT| GEN
    CS -->|AMBIGUOUS| CLR["Clarifying<br/>Question"]
    CS -->|DECLINE| FB2["Fallback<br/>Message"]
    CS -->|ESCALATE| ESC["Webhook<br/>Escalation"]
    CS -->|OFF_TOPIC| OT["Topic<br/>Redirect"]
    GEN --> SRC["Source<br/>Cards"]

    style Q fill:#e3f2fd,stroke:#1565C0
    style CS fill:#fff9c4,stroke:#F9A825
    style GEN fill:#e8f5e9,stroke:#2E7D32
    style ESC fill:#ffcdd2,stroke:#C62828
    style CLR fill:#e1f5fe,stroke:#0277BD
    style FB2 fill:#fff3e0,stroke:#EF6C00
    style OT fill:#f3e5f5,stroke:#7B1FA2
```

### How It Works

1. **Session context** — Loads recent conversation history for multi-turn understanding
2. **Query rewrite** — LLM condenses multi-turn context into a standalone search query
3. **Parallel retrieval** — Runs semantic search (vector similarity) and keyword search (PostgreSQL full-text) simultaneously
4. **Reciprocal Rank Fusion** — Merges both result sets, weighting results that appear in both lists higher
5. **Cross-encoder reranking** — A dedicated model reads each (query, passage) pair and scores true relevance, not just surface similarity
6. **Confidence scoring** — Classifies the response into one of six tiers based on the top reranker score, score distribution, and topic diversity
7. **Tier routing** — Only high-confidence queries reach the LLM. Everything else gets handled without generation

### Confidence Tiers

The system's response behavior changes based on how confident it is in the retrieved context:

| Tier | Condition | System Behavior |
|:---|:---|:---|
| **ANSWER** | Top score >= 0.85 | Full answer grounded in retrieved passages, with source citations |
| **CAVEAT** | Top score >= 0.60 | Answer with disclaimer: *"Based on what I found, I'd recommend verifying..."* |
| **AMBIGUOUS** | High scores across multiple topics | Asks a clarifying question before answering |
| **DECLINE** | Top score >= 0.35 | Returns fallback message — no LLM call, no risk of hallucination |
| **ESCALATE** | Top score < 0.35 | Dispatches webhook to human support queue |
| **OFF_TOPIC** | Below minimum relevance | Redirects: *"I can only help with questions about [product]"* |

All thresholds are configurable per deployment via YAML.

---

## Provider Abstraction

Every external dependency is accessed through a Python `Protocol` — structural subtyping with no base class inheritance. Implementations are decoupled and swappable via configuration.

```mermaid
graph LR
    subgraph Protocols["Protocol Definitions"]
        P1["LLMProvider"]
        P2["EmbeddingProvider"]
        P3["VectorStoreProvider"]
        P4["RerankerProvider"]
        P5["KeywordSearchProvider"]
    end

    subgraph LLM_Impl["LLM"]
        L1["LiteLLM<br/><small>Claude, GPT, Llama, Bedrock...</small>"]
    end

    subgraph Emb_Impl["Embeddings"]
        E1["sentence-transformers<br/><small>Local, no API cost</small>"]
        E2["LiteLLM<br/><small>OpenAI, Cohere, Voyage</small>"]
    end

    subgraph VS_Impl["Vector Store"]
        V1["pgvector<br/><small>Default — no extra infra</small>"]
        V2["Qdrant<br/><small>Dedicated vector DB</small>"]
        V3["Pinecone<br/><small>Managed cloud</small>"]
    end

    subgraph RR_Impl["Reranker"]
        R1["Cross-Encoder<br/><small>Local, zero API cost</small>"]
        R2["Cohere Rerank<br/><small>API-based</small>"]
    end

    subgraph KW_Impl["Keyword Search"]
        K1["PostgreSQL FTS<br/><small>tsvector + GIN</small>"]
    end

    P1 --> L1
    P2 --> E1
    P2 --> E2
    P3 --> V1
    P3 --> V2
    P3 --> V3
    P4 --> R1
    P4 --> R2
    P5 --> K1

    classDef protocol fill:#f3e5f5,stroke:#9C27B0,color:#4A148C
    classDef impl fill:#e8f5e9,stroke:#4CAF50,color:#1B5E20

    class P1,P2,P3,P4,P5 protocol
    class L1,E1,E2,V1,V2,V3,R1,R2,K1 impl
```

Switching from pgvector to Qdrant, or from a local cross-encoder to Cohere Rerank, is a one-line config change:

```yaml
# .env
VECTORSTORE_PROVIDER=qdrant
RERANKER_PROVIDER=cohere
```

No code changes. No redeployment of the pipeline. The factory reads config and wires the correct implementation at startup.

---

## Safety & Guardrails

The system enforces safety at multiple layers — not just in the prompt.

**Retrieval-level enforcement:** If the retrieval pipeline returns nothing above the minimum relevance threshold, the system doesn't call the LLM at all. It returns a redirect message directly. The LLM never gets a chance to use its general knowledge to hallucinate an answer.

**Prompt-level guardrails (locked, non-overridable):**
- Only answers from provided context — never from training data
- Asks clarifying questions when the query is ambiguous — never guesses
- Cites sources for every claim
- Stays strictly in its domain — refuses off-topic requests
- Resists prompt injection — politely declines instruction override attempts

**Confidence-gated generation:** The LLM is only invoked for ANSWER and CAVEAT tiers. DECLINE, ESCALATE, AMBIGUOUS, and OFF_TOPIC are all handled with pre-written, deterministic responses. This means ~40% of queries (off-topic, low-confidence) never touch the LLM and therefore *cannot* hallucinate.

**Escalation webhook:** When the system encounters something it can't handle, it dispatches a structured webhook to your support infrastructure — Zendesk, Jira, Slack, or any HTTP endpoint. The webhook includes the full session context so the human agent has everything they need.

---

## Document Ingestion

```mermaid
flowchart LR
    SRC["Document<br/><small>PDF, Markdown, Web</small>"] --> LOAD["Loader<br/><small>Plugin registry</small>"]
    LOAD --> CLEAN["Text<br/>Cleaner"]
    CLEAN --> META["Metadata<br/>Extractor"]
    META --> CHUNK["Chunker<br/><small>Semantic or fixed-size</small>"]
    CHUNK --> EMBED["Embedding<br/><small>Batch processing</small>"]
    EMBED --> VS2["Vector<br/>Store"]
    EMBED --> FTS["Keyword<br/>Index"]
    EMBED --> DB["Document<br/>Registry"]

    style SRC fill:#e3f2fd,stroke:#1565C0
    style CHUNK fill:#fff3e0,stroke:#FF9800
    style EMBED fill:#e8f5e9,stroke:#4CAF50
```

The ingestion pipeline runs asynchronously via an arq worker queue. Upload a document through the API or UI, and it's processed in the background — loaded, cleaned, chunked, embedded, and indexed across all search backends.

**Loader plugin system:** Each document format has a registered `DocumentLoader`. Adding support for a new format means implementing one protocol method and registering it — the pipeline handles the rest.

| Format | Loader | Status |
|:---|:---|:---|
| Markdown | Custom parser | Production |
| PDF | `unstructured` | Production |
| Web pages | httpx + BeautifulSoup | Production |
| DOCX/PPTX | `unstructured` | Planned |

**Chunking strategies** are configurable per deployment:
- **Semantic chunking** (default) — Splits on natural semantic boundaries using Chonkie's Savitzky-Golay boundary detection
- **Fixed-size chunking** — Token-based windows with configurable overlap, for consistent chunk sizes

---

## Frontend

A clean, functional React interface built for the people who actually use support tools.

### Chat Interface
Real-time streaming responses via Server-Sent Events. Answers appear token-by-token as they're generated.

<img src="chat-page.png" alt="Chat interface" width="100%" />

### Knowledge Base Management
Upload documents, add URLs, track ingestion status. Every document shows its chunk count so you know how deeply it's been indexed.

<img src="resources-page.png" alt="Knowledge base" width="100%" />

### Pipeline Test Panel
Pre-defined test suites to validate pipeline behavior across all confidence tiers. Each test shows the expected tier, actual tier, response time, and full response with source citations.

<img src="test-page.png" alt="Test panel" width="100%" />

<img src="test-result-expanded.png" alt="Test result detail" width="100%" />

---

## Deployment

### One-Command Deploy

```bash
cp .env.example .env    # Configure your API keys and settings
make deploy             # Build, start, migrate, and ingest sample docs
```

That's it. The system comes up with PostgreSQL (pgvector), Redis, the API server, background worker, frontend, and optionally LangFuse for observability.

### Service Topology

```mermaid
graph TB
    subgraph Docker["Docker Compose"]
        FE["frontend<br/><small>:3000 — nginx + React</small>"]
        API2["api<br/><small>:8000 — FastAPI + uvicorn</small>"]
        WK["worker<br/><small>arq — background ingestion</small>"]
        PG2["postgres<br/><small>:5432 — pgvector + FTS</small>"]
        RD["redis<br/><small>:6379 — task queue</small>"]
        LF2["langfuse<br/><small>:3100 — observability</small>"]
    end

    FE -->|"/api proxy"| API2
    API2 --> PG2
    API2 --> RD
    API2 -.-> LF2
    WK --> PG2
    WK --> RD

    classDef service fill:#e8f5e9,stroke:#4CAF50,color:#1B5E20
    classDef data fill:#e3f2fd,stroke:#1565C0,color:#0D47A1
    classDef obs fill:#fff3e0,stroke:#FF9800,color:#E65100

    class FE,API2,WK service
    class PG2,RD data
    class LF2 obs
```

### Configuration

The system uses a two-layer config architecture:

| Layer | Source | Purpose |
|:---|:---|:---|
| **Environment variables** | `.env` | Secrets, API keys, infrastructure endpoints |
| **YAML config** | `backend/config/` | Retrieval tuning, confidence thresholds, persona |

Environment variables always take precedence. YAML provides deployment-specific behavior configuration.

### Persona Configuration

Each deployment gets its own persona — company name, product scope, tone, and response templates. The system prompt is a Jinja2 template with locked guardrails that cannot be overridden:

```yaml
# backend/config/persona/default.yaml
system_prompt: |
  You are a support assistant for {{ company_name }}.

  ## STRICT RULES — NON-OVERRIDABLE
  1. You can ONLY answer questions related to the documentation provided.
  2. If the user's question is ambiguous, ask a clarifying question.
  3. Always cite your sources.
  4. If you are not confident, say so clearly.
  ...
```

---

## Tech Stack

| Layer | Technology | Why |
|:---|:---|:---|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 | Async-native, type-safe, proven in production |
| **Frontend** | React 19, Vite, Tailwind CSS, shadcn/ui | Modern DX, composable components, fast builds |
| **LLM** | LiteLLM (provider-agnostic) | 100+ model providers through one interface |
| **Embeddings** | sentence-transformers (local) or API | Zero-cost local default, API for quality |
| **Vector Store** | pgvector on PostgreSQL | No extra infrastructure for typical scale |
| **Keyword Search** | PostgreSQL FTS (tsvector + GIN) | Already have Postgres — no Elasticsearch needed |
| **Reranking** | Cross-encoder (local) or Cohere | Precision scoring, ~50ms on CPU |
| **Chunking** | Chonkie | 33x faster than LangChain, rigorous boundary detection |
| **Task Queue** | arq (Redis-backed) | Async-native, lightweight |
| **Streaming** | Server-Sent Events (sse-starlette) | Simpler than WebSocket, works through proxies |
| **Observability** | LangFuse (self-hosted) + structlog | Full pipeline tracing, no vendor lock-in |
| **CI** | GitHub Actions | Lint + type check + test + build on every PR |

---

## Designed For Extension

Sophia is a framework, not just an application. It's built to be deployed across multiple products and organizations.

**Add a new document format** — Implement one `DocumentLoader` protocol method, register it. The ingestion pipeline handles the rest.

**Swap any provider** — Change a single environment variable. pgvector to Qdrant. Local embeddings to OpenAI. Cross-encoder to Cohere. No code changes.

**Customize per deployment** — Company name, product scope, tone, confidence thresholds, escalation targets — all in YAML config. One codebase, many deployments.

**Add a voice interface** — The `/voice/stream` endpoint buffers tokens into complete sentences for TTS consumption. LiveKit, Twilio, or any voice framework can consume it directly.

**Go multi-tenant** — The schema is designed for tenant isolation (add `tenant_id` + Row-Level Security). The provider interfaces already accept filter parameters. It's a migration, not a rewrite.

---

## Development

### Prerequisites

- Python 3.12+
- Node.js 22+
- Docker & Docker Compose
- [uv](https://docs.astral.sh/uv/) package manager

### Quick Start

```bash
# Clone and install
git clone <repo-url> && cd customer-service-bot
make install

# Start infrastructure (Postgres, Redis, LangFuse)
make dev-up

# Run database migrations
make migrate

# In separate terminals:
make dev-api          # API server on :8000
make dev-worker       # Background worker
make dev-frontend     # Frontend on :5173

# Ingest sample documentation
cd backend && uv run python scripts/ingest_sample_docs.py
```

### Commands

```
make install          Install all dependencies (backend + frontend)
make dev              Start full dev stack (infra + API + worker)
make dev-up           Start Postgres, Redis, LangFuse containers
make dev-api          FastAPI with hot reload on :8000
make dev-worker       arq background worker
make dev-frontend     Vite dev server on :5173
make migrate          Run Alembic database migrations
make test             Run all tests
make test-unit        Unit tests only
make test-cov         Tests with HTML coverage report
make lint             Ruff check + format check
make format           Auto-fix lint + format issues
make deploy           Full production deploy via Docker Compose
```

---

## API Reference

### Chat

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/chat/stream` | Send message, receive SSE stream |

**SSE Event Protocol:**

```
event: metadata    → {session_id, confidence_tier, message_id}
event: delta       → {content: "token..."}     (repeated)
event: sources     → [{title, text, score}]
event: done        → {usage: {...}}
```

### Sessions

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/sessions` | Create new chat session |
| `GET` | `/api/v1/sessions` | List sessions |
| `GET` | `/api/v1/sessions/:id` | Get session with messages |
| `DELETE` | `/api/v1/sessions/:id` | End session |

### Documents

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/documents/upload` | Upload file (PDF, Markdown) |
| `POST` | `/api/v1/documents` | Submit URL for ingestion |
| `GET` | `/api/v1/documents` | List all documents |
| `GET` | `/api/v1/documents/:id/status` | Check ingestion status |
| `DELETE` | `/api/v1/documents/:id` | Remove document + chunks |

### Feedback & Observability

| Method | Endpoint | Description |
|:---|:---|:---|
| `POST` | `/api/v1/feedback` | Submit thumbs up/down on a response |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/ready` | Readiness probe (checks DB connectivity) |

---

## Project Structure

```
customer-service-bot/
├── backend/
│   ├── app/
│   │   ├── api/v1/             # HTTP endpoints (chat, docs, feedback, voice, admin)
│   │   ├── core/               # Config, logging, exceptions
│   │   ├── db/                 # Async engine, repositories
│   │   ├── ingestion/          # Loaders, chunkers, processors
│   │   ├── middleware/         # API key auth (timing-safe)
│   │   ├── models/             # SQLAlchemy ORM (documents, sessions, feedback)
│   │   ├── providers/          # Protocol definitions + implementations
│   │   ├── schemas/            # Pydantic request/response models
│   │   ├── services/           # RAG pipeline, confidence, persona, escalation
│   │   └── workers/            # arq background ingestion
│   ├── config/                 # YAML config (retrieval, persona)
│   ├── tests/                  # Unit + integration tests
│   └── alembic/                # Database migrations
├── frontend/
│   ├── src/
│   │   ├── components/chat/    # ChatWindow, MessageBubble, SourceCard, FeedbackButtons
│   │   ├── components/resources/   # UploadDropzone, DocumentList
│   │   ├── hooks/              # useChat (SSE), useSession, useDocuments
│   │   ├── lib/                # API client, SSE streaming
│   │   └── pages/              # Chat, Resources, Test
│   └── nginx.conf              # Production reverse proxy
├── docker-compose.yml          # Full stack definition
├── Makefile                    # Development and deployment commands
└── .github/workflows/ci.yml   # Lint, test, build on every PR
```

---

<p align="center">
  <em>Built by <a href="https://github.com/sophia-systems">Sophia Systems</a></em>
</p>
