# Smart Support System

An AI-powered customer support dashboard that helps support teams work faster and smarter.

## What It Does

Smart Support System analyzes customer messages through an AI workflow and gives support agents everything they need to respond quickly and effectively.

The AI processes each message and returns:

- **Intent** - What the customer wants (refund, shipping, product inquiry, complaint, general)
- **Sentiment** - How the customer feels (positive, neutral, negative)
- **Priority** - How urgent the ticket is (low, medium, high, urgent)
- **Product Recommendations** - Products the customer might need
- **Response** - A professionally drafted reply
- **Escalation** - Whether a human agent needs to step in

## Who It's For

This is an internal tool for support teams and business owners, not a customer-facing system.

- **Support Agents** - Work faster with AI-analyzed tickets and draft responses
- **Support Managers** - Monitor sentiment trends, ticket stats, and escalation rates
- **Business Owners** - Understand what customers are complaining about and track overall satisfaction

## Tech Stack

### Backend
- **Python 3.12** - Core language
- **FastAPI** - REST API framework
- **LangGraph** - AI workflow orchestration
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Development database
- **OpenRouter** - LLM API (Gemma 4 31B)

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - API client

## Features

### Dashboard
- Real-time ticket statistics (total, open, escalated, escalation rate)
- Sentiment distribution (positive, neutral, negative)
- AI message analyzer with live results
- Save analyzed messages as tickets
- Recent tickets view
- AI-generated executive summary of recent tickets
- Intent distribution breakdown

### Products
- Browse 1,465 products with real data
- Search products by name or description
- Filter by category, price range
- Sort by price, stock, or date added
- Pagination
- Product detail modal with full information

### Tickets
- Full ticket management system
- 8,470 real support tickets
- Filter by status (new, in_progress, resolved, closed)
- Filter by intent (refund, shipping, product_inquiry, complaint, general)
- Search tickets by message or customer name
- View AI analysis for each ticket (intent, sentiment, priority, reasoning, response)
- Update ticket status
- Create new tickets with automatic AI analysis

### AI Workflow

The system uses a LangGraph state machine with 6 processing nodes:

1. **Classify Intent** - Determines what the customer wants
2. **Analyze Sentiment** - Detects emotional tone
3. **Assign Priority** - Sets urgency level based on intent and sentiment
4. **Recommend Products** - Suggests relevant products for product inquiries
5. **Generate Response** - Creates a professional, empathetic reply
6. **Check Escalation** - Decides if a human agent needs to intervene

## Getting Started

### Prerequisites

- Python 3.12
- Node.js 18+
- npm

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your OpenRouter API key
cp .env.example .env
# Edit .env with your API key

# Seed the database with real data
python scripts/seed_real_data.py

# Start the server
uvicorn app.main:app --reload