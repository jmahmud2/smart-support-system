# Smart Support System

An AI-powered customer support dashboard for support teams and business owners.

## What It Does

Smart Support System analyzes customer messages through an AI workflow and gives support teams everything they need to respond faster.

The AI processes each message and returns:

- **Intent** - What the customer wants (refund, shipping, product inquiry, complaint, general)
- **Sentiment** - How the customer feels (positive, neutral, negative)
- **Priority** - How urgent the ticket is (low, medium, high, urgent)
- **Product Recommendations** - Products the customer might need
- **Response** - A professionally drafted reply
- **Escalation** - Whether a human agent needs to step in

## Who It's For

This is an internal tool for support teams and business owners.

- **Support Agents** - Work faster with AI-analyzed tickets and draft responses
- **Support Managers** - Monitor sentiment trends, ticket stats, and escalation rates
- **Business Owners** - Understand what customers are complaining about and track overall satisfaction


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

## Getting Started

### Prerequisites

- Python 3.12
- Node.js 18+
- npm

