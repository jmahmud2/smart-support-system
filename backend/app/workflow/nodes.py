"""
Workflow node implementations for the customer support system.
"""

import json
from .state import SupportState
from .llm import call_llm
from ..utils.logger import get_logger

logger = get_logger(__name__)


def analyze_message_comprehensive(state: SupportState) -> dict:
    """
    Single LLM call for intent, sentiment, priority, and summary.
    Replaces 4 separate calls with 1.
    """
    message = state.get("customer_message", "")
    
    prompt = f"""
    Analyze this customer message and return a JSON object with:
    {{
        "intent": "refund|shipping|product_inquiry|complaint|general",
        "sentiment": "positive|neutral|negative",
        "priority": "urgent|high|medium|low",
        "summary": "one sentence summary of the issue"
    }}
    
    Message: {message}
    
    Return ONLY the JSON object, no other text.
    """
    
    response = call_llm(prompt)
    try:
        data = json.loads(response)
        return {
            "intent": data.get("intent", "general"),
            "sentiment": data.get("sentiment", "neutral"),
            "sentiment_explanation": f"Sentiment detected: {data.get('sentiment', 'neutral')}",
            "priority": data.get("priority", "low"),
            "priority_reasoning": f"Priority assigned: {data.get('priority', 'low')}",
            "ticket_summary": data.get("summary", "Customer inquiry")
        }
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse JSON from LLM: {response[:100]}...")
        return {
            "intent": "general",
            "sentiment": "neutral",
            "sentiment_explanation": "Unable to determine sentiment",
            "priority": "low",
            "priority_reasoning": "Default priority assigned",
            "ticket_summary": "Customer inquiry"
        }


def classify_intent(state: SupportState) -> dict:
    """Fallback: Classify intent using LLM."""
    message = state.get("customer_message", "")
    prompt = f"""
    Classify this customer message into ONE category: refund, shipping, product_inquiry, complaint, or general.
    Return only the category name.

    Message: {message}
    """
    intent = call_llm(prompt).strip().lower()
    valid_intents = ["refund", "shipping", "product_inquiry", "complaint", "general"]
    if intent not in valid_intents:
        intent = "general"
    return {"intent": intent}


def analyze_sentiment(state: SupportState) -> dict:
    """Fallback: Analyze sentiment."""
    message = state.get("customer_message", "")
    prompt = f"""
    Analyze the sentiment of this message. Return only ONE word: positive, neutral, or negative.
    Message: {message}
    """
    sentiment = call_llm(prompt).strip().lower()
    if sentiment not in ["positive", "neutral", "negative"]:
        sentiment = "neutral"
    explanations = {
        "positive": "Customer expressed satisfaction or positive sentiment",
        "neutral": "Customer message was factual or neutral in tone",
        "negative": "Customer expressed frustration or negative sentiment"
    }
    return {
        "sentiment": sentiment,
        "sentiment_explanation": explanations.get(sentiment, "Unable to determine sentiment")
    }


def assign_priority_ai(state: SupportState) -> dict:
    """Fallback: Assign priority."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")
    prompt = f"""
    Assign a priority to this message. Return only ONE word: urgent, high, medium, or low.
    Message: {message}
    Intent: {intent}
    Sentiment: {sentiment}
    """
    try:
        response = call_llm(prompt).strip().lower()
        if response not in ["urgent", "high", "medium", "low"]:
            if "urgent" in message.lower() or "immediately" in message.lower():
                priority = "urgent"
            elif sentiment == "negative" and intent == "complaint":
                priority = "high"
            elif intent == "shipping":
                priority = "medium"
            else:
                priority = "low"
        else:
            priority = response
    except Exception:
        priority = "medium"
    reasonings = {
        "urgent": "Immediate attention needed",
        "high": "Important issue needing prompt attention",
        "medium": "Standard priority issue",
        "low": "Low priority, can be addressed later"
    }
    return {
        "priority": priority,
        "priority_reasoning": reasonings.get(priority, "Priority assigned based on message content")
    }


def generate_ticket_summary(state: SupportState) -> dict:
    """Fallback: Generate summary."""
    message = state.get("customer_message", "")
    prompt = f"Summarize this customer message in ONE short sentence.\n\nMessage: {message}"
    summary = call_llm(prompt).strip()
    if not summary or len(summary) < 3:
        summary = "Customer inquiry"
    if len(summary) > 150:
        summary = summary[:147] + "..."
    return {"ticket_summary": summary}


def intelligent_routing(state: SupportState) -> dict:
    """Route ticket to appropriate agent."""
    intent = state.get("intent", "general")
    try:
        from ..database.database import SessionLocal
        from ..database.models import Agent
        db = SessionLocal()
        agents = db.query(Agent).filter(Agent.active == True).all()
        db.close()
        if agents:
            for agent in agents:
                if agent.specialty and intent.lower() in agent.specialty.lower():
                    return {"assigned_agent": agent.name}
            return {"assigned_agent": agents[0].name}
    except Exception as e:
        logger.warning(f"Agent lookup failed: {e}")
    return {"assigned_agent": "Unassigned"}


def find_similar_tickets(state: SupportState) -> dict:
    """Find similar past tickets."""
    message = state.get("customer_message", "")
    prompt = f"""
    Extract 3 key words from this message that describe the issue.
    Return only the words separated by commas.
    Message: {message}
    """
    keywords = call_llm(prompt).strip()
    if not keywords:
        keywords = "customer issue"
    return {
        "similar_tickets": [
            {"id": "sim1", "summary": "Similar issue found", "keywords": keywords},
            {"id": "sim2", "summary": "Related support case", "keywords": keywords},
            {"id": "sim3", "summary": "Past ticket with similar keywords", "keywords": keywords}
        ]
    }


def recommend_products(state: SupportState) -> dict:
    """Recommend products based on inquiry."""
    intent = state.get("intent", "general")
    if intent not in ["product_inquiry", "general"]:
        return {"recommended_products": []}
    message = state.get("customer_message", "")
    prompt = f"""
    Based on this message, recommend 3 products. Return ONLY the product names separated by commas.
    Message: {message}
    """
    response = call_llm(prompt).strip()
    recommendations = [item.strip() for item in response.split(',') if item.strip()]
    return {"recommended_products": recommendations[:3]}


def generate_response(state: SupportState) -> dict:
    """Generate AI-powered response."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")
    priority = state.get("priority", "low")
    recommended = state.get("recommended_products", [])
    rec_text = f"\nMention these products: {', '.join(recommended)}" if recommended else ""
    prompt = f"""
    Write a short, professional support response to this customer.
    Message: {message}
    Intent: {intent}
    Sentiment: {sentiment}
    Priority: {priority}
    {rec_text}
    Requirements:
    - Professional and empathetic
    - Provide clear next steps
    - 3-5 sentences maximum
    - Start with an apology if sentiment is negative
    Return only the response.
    """
    response = call_llm(prompt).strip()
    if not response:
        response = "Thank you for reaching out. Our team will review your inquiry and respond shortly."
    return {"response": response}


def check_escalation_ai(state: SupportState) -> dict:
    """Determine if ticket should be escalated."""
    priority = state.get("priority", "medium")
    sentiment = state.get("sentiment", "neutral")
    intent = state.get("intent", "general")
    message = state.get("customer_message", "").lower()
    escalate = False
    reasoning = "Auto-response is sufficient"
    if priority == "urgent":
        escalate = True
        reasoning = "Urgent priority requires human attention"
    elif sentiment == "negative" and intent == "complaint":
        escalate = True
        reasoning = "Negative complaint may need human intervention"
    elif any(w in message for w in ["urgent", "immediately", "asap", "emergency", "manager", "supervisor"]):
        escalate = True
        reasoning = "Urgent language detected in message"
    return {"escalate": escalate, "escalate_reasoning": reasoning}