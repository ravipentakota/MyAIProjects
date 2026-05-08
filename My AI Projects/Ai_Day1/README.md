# Amzur AI Chat

Multi-user conversational AI platform with persistent threads, authentication, multi-modal input, and RAG capabilities.

## Project Structure

```
/
├── frontend/          # React + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── lib/       # API client
│   │   └── types/     # Shared TypeScript types
│   ├── .env.example   # Frontend environment variables
│   └── package.json
│
└── backend/           # FastAPI + Python
    ├── app/
    │   ├── api/       # Route handlers
    │   ├── services/  # Business logic
    │   ├── models/    # SQLAlchemy ORM
    │   ├── schemas/   # Pydantic models
    │   ├── ai/        # AI layer (LLM, RAG, etc.)
    │   ├── db/        # Database session
    │   └── core/      # Configuration
    ├── main.py        # FastAPI entry point
    ├── requirements.txt
    └── .env.example   # Backend environment variables
```

## Tech Stack

- **Frontend:** React 19, TypeScript, Tailwind CSS, Vite
- **Backend:** FastAPI, Python 3.11+, PostgreSQL, SQLAlchemy 2.0
- **AI Orchestration:** LangChain (LCEL), LiteLLM proxy
- **Authentication:** JWT + httpOnly cookies, Google OAuth 2.0
- **Vector Store:** ChromaDB (for RAG)
- **Models:** gpt-4o, gemini-2.5-flash (via LiteLLM proxy)

## Getting Started

### Backend Setup

1. Install Python 3.11+
2. Create a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Run the server:
   ```bash
   python main.py
   ```

### Frontend Setup

1. Install Node.js 18+
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your configuration
   ```
4. Start development server:
   ```bash
   npm run dev
   ```

## Configuration

### Backend Environment Variables

See `backend/.env.example` for all required environment variables.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `LITELLM_PROXY_URL`: Amzur LiteLLM proxy endpoint
- `LITELLM_API_KEY`: API key for LiteLLM proxy
- `SECRET_KEY`: JWT signing key
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`: For OAuth (optional)

### Frontend Environment Variables

See `frontend/.env.example` for configuration.

Key variable:
- `VITE_API_BASE_URL`: Backend API endpoint (default: http://localhost:8000/api)

## Architecture Principles

- **Single AI gateway:** All LLM calls route through LiteLLM proxy
- **Layered services:** API → Services → Models (no business logic in routes)
- **Type safety:** Full TypeScript in frontend, type annotations in backend
- **Security:** JWT in httpOnly cookies, server-side auth checks
- **Streaming:** All user-facing LLM responses streamed incrementally

## Development

### Code Quality

- Backend: `ruff` for linting, `black` for formatting
- Frontend: `eslint` for linting, `prettier` for formatting (via Vite)
- All Python code must have type annotations
- TypeScript strict mode enabled

### Testing

- Backend: `pytest` with `pytest-asyncio`
- Frontend: Vitest + React Testing Library

### Git Workflow

Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`

## Resources

- [Project Instructions](./github/copilot-instructions.md)
- Backend API docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`
