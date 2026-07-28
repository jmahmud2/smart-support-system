# Smart Support System

AI-powered customer support platform with intelligent ticket routing, sentiment analysis, and automated responses.

## Tech Stack

**Backend:** FastAPI, SQLite, LangGraph, OpenRouter (Gemini 2.0), ChromaDB, JWT  
**Frontend:** React 18, Vite, Tailwind CSS

## Setup

### Backend

cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

Create .env file (see below). Initialize DB:

bash
python -c "from app.database.database import init_db; init_db()"
Run:

bash
uvicorn app.main:app --reload

### Frontend

cd frontend
npm install

Create .env:

text
VITE_API_URL=http://localhost:8000
Run:

bash
npm run dev
Access: http://localhost:5173

### Environment Variables

Backend (.env)

# Database
DATABASE_URL

# OpenRouter API (for AI workflow - get your key from https://openrouter.ai/)

OPENROUTER_API_KEY
OPENROUTER_BASE_URL
OPENROUTER_MODEL

# App Settings
SECRET_KEY
DEBUG
ALLOWED_ORIGINS

# Rate Limiting
RATE_LIMIT_PER_MINUTE
RATE_LIMIT_RETRIES
RATE_LIMIT_BACKOFF

RESEND_API_KEY
RESEND_FROM_EMAIL

# Pagination
DEFAULT_PAGE_LIMIT
MAX_PAGE_LIMIT

# RAG Configuration
EMBEDDING_MODEL
CHROMA_PERSIST_DIR
CHROMA_COLLECTION_NAME

# LLM Fallback Messages
FALLBACK_RESPONSE
FALLBACK_RATE_LIMIT

# Demo Users (optional - for development only)
DEMO_AGENT_EMAIL
DEMO_AGENT_PASSWORD
DEMO_AGENT_NAME
DEMO_MANAGER_EMAIL
DEMO_MANAGER_PASSWORD
DEMO_MANAGER_NAME
DEMO_ADMIN_EMAIL
DEMO_ADMIN_PASSWORD
DEMO_ADMIN_NAME

# Email (Optional - for email integration)
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_FROM_EMAIL

Frontend (.env)

VITE_API_URL

### API Endpoints

Method	Endpoint	Description
POST	/api/auth/login	Login
GET	/api/products	List products
POST	/api/support/tickets	Create ticket
GET	/api/support/tickets	List tickets
GET	/api/support/stats	Support stats
GET	/health	Health check
Full API docs available at /docs when running.

### AI Workflow

The system uses LangGraph to orchestrate the AI pipeline:

Classify intent → 2. Analyze sentiment → 3. Assign priority → 4. Generate summary → 5. Route to agent → 6. Find similar tickets → 7. Recommend products → 8. Generate response → 9. Check escalation

Additional AI features: reply options, quality scoring, RAG knowledge search, churn prediction, follow-up detection, language detection, resolution time prediction.

### 

AI-generated responses with sentiment-aware tone

Smart agent routing

RAG knowledge base retrieval

Churn prediction

SLA tracking

Customer order/ticket history

Auto-reply to new tickets

Duplicate ticket detection & merging

Email notifications (Resend)

Dark mode