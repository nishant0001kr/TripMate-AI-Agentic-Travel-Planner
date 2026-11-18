# TripMate AI

An agentic travel-planning application built with **LangGraph**, **Model Context
Protocol (MCP)**, **FastAPI**, and **Groq**. TripMate converts a natural-language
request into a practical itinerary by coordinating specialist agents, validating
the request with guardrails, and pausing for human approval before finalizing the
plan.

## Why this project stands out

- **Supervisor architecture** dynamically selects only the agents needed for a request.
- **MCP integrations** connect the workflow to live hotel, aviation, and weather data.
- **Input guardrails** reject unrelated or unsafe requests before expensive work begins.
- **Human-in-the-loop (HITL)** lets users approve a draft or request revisions.
- **Durable LangGraph state** supports PostgreSQL in production and zero-config in-memory state locally.
- **Graceful degradation** keeps the workflow useful when an optional live-data API is unavailable.

## Architecture

```mermaid
flowchart LR
    U[User request] --> G[Input guardrail]
    G -->|Blocked| R[Safe response]
    G -->|Allowed| S[Supervisor]
    S --> F[Flight agent]
    S --> H[Hotel agent]
    S --> W[Weather agent]
    S --> B[Budget agent]
    F --> I[Itinerary agent]
    H --> I
    W --> I
    B --> I
    I --> A{Human approval}
    A -->|Approve| P[Final plan]
    A -->|Feedback| P
```

The supervisor extracts trip constraints and builds a route through the
specialist agents. LangGraph checkpoints the state before pausing at the approval
interrupt. The approval endpoint resumes the same thread with the user's decision
and optional feedback.

## Agent responsibilities

| Agent | Responsibility | Integration |
|---|---|---|
| Supervisor | Guardrails, constraint extraction, dynamic routing | Groq LLM |
| Flight | Airports, airlines, route guidance | AviationStack MCP |
| Hotel | Accommodation and neighborhood research | Tavily MCP |
| Weather | Current conditions and forecast | Custom OpenWeather MCP server |
| Budget | Cost categories, risks, and feasibility | Groq LLM |
| Itinerary | Produces a reviewable day-by-day draft | Groq LLM |
| Final response | Applies human approval or revision feedback | Groq LLM |

## Technology stack

- Python 3.12
- FastAPI and Uvicorn
- LangGraph and LangChain
- Model Context Protocol (`mcp`, `langchain-mcp-adapters`)
- Groq (`openai/gpt-oss-120b`)
- PostgreSQL checkpointer for production
- Jinja2, HTML, CSS, and JavaScript frontend

## Run locally on Windows

### 1. Create the environment

```powershell
git clone https://github.com/nishant0001kr/TripMate-AI-Agentic-Travel-Planner.git
cd Trip_Agentic
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install uv
```

`uv` provides `uvx`, which launches the AviationStack MCP server.

### 2. Configure credentials

```powershell
Copy-Item .env.example .env
notepad .env
```

```env
GROQ_API_KEY=your_groq_key
GROQ_MODEL=openai/gpt-oss-120b
TAVILY_API_KEY=your_tavily_key
AVIATION_STACK_API_KEY=your_aviationstack_key
OPENWEATHER_API_KEY=your_openweather_key

# Optional: omit for in-memory state during local development.
# DATABASE_URL=postgresql://user:password@localhost:5432/tripmate
```

Only `GROQ_API_KEY` is required for the core planning workflow. Missing optional
provider keys activate clearly labelled fallback guidance instead of exposing a
server error. Never commit `.env`.

### 3. Start the application

```powershell
python app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Example demo

Try this prompt:

> Plan a five-day trip from Delhi to Tokyo for two people with a ₹2,50,000
> budget. We enjoy food, technology, and quiet neighborhoods.

The application will:

1. Validate that the request is travel-related.
2. Extract origin, destination, duration, budget, and preferences.
3. Select the relevant specialist agents.
4. Create a budget-aware draft itinerary.
5. Pause for approval or revision feedback.
6. Resume the same LangGraph thread and produce the final plan.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service and feature health check |
| `POST` | `/api/travel` | Start a planning thread |
| `POST` | `/api/travel/approve` | Resume a paused thread with approval or feedback |

Start a plan:

```json
{
  "message": "Plan a three-day trip to Singapore under ₹80,000"
}
```

Approve or revise it:

```json
{
  "thread_id": "user_<generated-id>",
  "approved": false,
  "feedback": "Reduce the hotel cost and add more local food options."
}
```

## Project structure

```text
Trip_Agentic/
├── app.py                         # FastAPI routes and request models
├── backend.py                     # LangGraph agents, routing, HITL, persistence
├── mcp_client.py                  # MCP clients and provider isolation
├── custom_weather_mcp_server.py   # Local OpenWeather MCP server
├── templates/                     # Web interface
├── static/                        # Browser JavaScript and styles
├── requirements.txt
└── .env.example                   # Safe configuration template
```

## Engineering decisions to discuss in an interview

- **Dynamic routing:** the supervisor avoids running irrelevant agents.
- **Fault isolation:** each MCP provider is loaded independently, so one broken
  integration does not prevent unrelated agents from running.
- **HITL resumability:** LangGraph `interrupt()` and `Command(resume=...)` model a
  reviewable workflow rather than a single opaque LLM call.
- **Environment portability:** PostgreSQL is optional locally but available for
  durable production threads.
- **Secret management:** real credentials stay in the ignored `.env`; only
  `.env.example` is version-controlled.
- **Model lifecycle:** the model is configured through `GROQ_MODEL`, making
  provider deprecations a configuration change instead of a code rewrite.

## Future improvements

- Add automated unit and integration tests for routing and approval flows.
- Add observability with LangSmith or OpenTelemetry.
- Cache provider responses and add retry/backoff policies.
- Containerize PostgreSQL for a one-command local durable environment.
- Add authentication and per-user thread ownership before production deployment.

## License and attribution

This project is based on
[`entbappy/Multi-Agent-System-using-LangGraph-MCP-Supervisor-Guardrails-HITL`](https://github.com/entbappy/Multi-Agent-System-using-LangGraph-MCP-Supervisor-Guardrails-HITL)
and retains its Apache License 2.0. The local-development fallback, current Groq
model migration, configuration hardening, and documentation improvements in this
repository were added as part of this implementation.
