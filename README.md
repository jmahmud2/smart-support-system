# Smart Support System

An AI-powered customer support dashboard for support teams and business owners.

---

## What It Does

Smart Support System analyzes customer messages through an AI workflow and gives support teams everything they need to respond faster.

The AI processes each message and returns:

- **Intent** - What the customer wants (refund, shipping, product inquiry, complaint, general)
- **Sentiment** - How the customer feels (positive, neutral, negative)
- **Priority** - How urgent the ticket is (low, medium, high, urgent)
- **Product Recommendations** - Products the customer might need
- **Response** - A professionally drafted reply
- **Escalation** - Whether a human agent needs to step in

---

## Who It's For

This is an internal tool for support teams and business owners.

- **Support Agents** - Work faster with AI-analyzed tickets and draft responses
- **Support Managers** - Monitor sentiment trends, ticket stats, and escalation rates
- **Business Owners** - Understand what customers are complaining about and track overall satisfaction

---

## Tech Stack

### Backend
- Python 3.12
- FastAPI
- LangGraph
- SQLAlchemy
- SQLite (development) / Supabase PostgreSQL (production)
- OpenRouter (Gemma 4 31B)

### Frontend
- React 18
- Vite
- Tailwind CSS
- React Router
- Axios

---

## Features

### Dashboard
- Real-time ticket statistics
- Sentiment distribution
- AI message analyzer with live results
- Save analyzed messages as tickets
- Recent tickets view
- AI-generated executive summary
- Intent distribution breakdown

### Products
- Browse 1,465 products with real data
- Search products by name or description
- Filter by category and price range
- Sort by price, stock, or date added
- Pagination
- Product detail modal

### Tickets
- Full ticket management
- 8,470 real support tickets
- Filter by status and intent
- Search tickets
- View AI analysis for each ticket
- Update ticket status
- Create new tickets with automatic AI analysis

### AI Workflow

The system uses a LangGraph state machine with 6 processing nodes:

1. Classify Intent
2. Analyze Sentiment
3. Assign Priority
4. Recommend Products
5. Generate Response
6. Check Escalation

---

## Getting Started

### Prerequisites

- Python 3.12
- Node.js 18+
- npm

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenRouter API key
python scripts/seed_real_data.py
uvicorn app.main:app --reload

Frontend Setup

cd frontend
npm install
npm run dev
Environment Variables
Create a .env file in the backend directory:

env

DATABASE_URL=sqlite:///./app.db
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemma-4-31b-it:free
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

Data

The system comes pre-seeded with:

1,465 real products with names, descriptions, prices, and categories

8,470 real support tickets with AI analysis results

10 categories including Electronics, Clothing, Home & Kitchen, and Books