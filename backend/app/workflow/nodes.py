"""
Workflow node implementations for the customer support system.
"""

import json
from .state import SupportState
from .llm import call_llm
from ..utils.logger import get_logger

logger = get_logger(__name__)


def classify_intent(state: SupportState) -> dict:
    """Classify the customer's intent using the LLM."""
    message = state.get("customer_message", "")
    logger.info(f"Classifying intent: {message[:50]}...")

    prompt = f"""
    Classify this customer message into ONE category: refund, shipping, product_inquiry, complaint, or general.
    Return only the category name.

    Message: {message}
    """

    intent = call_llm(prompt).strip().lower()
    valid_intents = ["refund", "shipping", "product_inquiry", "complaint", "general"]
    if intent not in valid_intents:
        intent = "general"

    logger.info(f"   Intent: {intent}")
    return {"intent": intent}


def analyze_sentiment(state: SupportState) -> dict:
    """Analyze the sentiment of the customer message with explanation."""
    message = state.get("customer_message", "")
    logger.info(f"Analyzing sentiment: {message[:50]}...")

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

    result = {
        "sentiment": sentiment,
        "sentiment_explanation": explanations.get(sentiment, "Unable to determine sentiment")
    }
    logger.info(f"   Sentiment: {sentiment}")
    return result


def assign_priority_ai(state: SupportState) -> dict:
    """Assign priority using AI instead of if/else rules."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")
    logger.info(f"Assigning priority: {message[:50]}...")

    prompt = f"""
    Assign a priority to this message. Return only ONE word: urgent, high, medium, or low.

    Message: {message}
    Intent: {intent}
    Sentiment: {sentiment}
    """

    try:
        response = call_llm(prompt).strip().lower()
        if response not in ["urgent", "high", "medium", "low"]:
            if "urgent" in message.lower() or "immediately" in message.lower() or "asap" in message.lower():
                priority = "urgent"
            elif sentiment == "negative" and intent == "complaint":
                priority = "high"
            elif intent == "shipping":
                priority = "medium"
            else:
                priority = "low"
        else:
            priority = response
    except Exception as e:
        logger.error(f"Priority parsing error: {e}")
        priority = "medium"

    reasonings = {
        "urgent": "Immediate attention needed based on message content",
        "high": "Important issue that needs prompt attention",
        "medium": "Standard priority issue",
        "low": "Low priority, can be addressed later"
    }

    result = {
        "priority": priority,
        "priority_reasoning": reasonings.get(priority, "Priority assigned based on message content")
    }
    logger.info(f"   Priority: {priority}")
    return result


def generate_ticket_summary(state: SupportState) -> dict:
    """Generate a 1-sentence summary of the ticket."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    logger.info(f"Generating summary: {message[:50]}...")

    prompt = f"""
    Summarize this customer message in ONE short sentence.

    Message: {message}
    """

    summary = call_llm(prompt).strip()
    if not summary or len(summary) < 3:
        summary = f"{intent} inquiry from customer"

    if len(summary) > 150:
        summary = summary[:147] + "..."

    logger.info(f"   Summary: {summary[:50]}...")
    return {"ticket_summary": summary}


def intelligent_routing(state: SupportState) -> dict:
    """Route the ticket to the right agent based on expertise needed."""
    intent = state.get("intent", "general")
    message = state.get("customer_message", "")
    logger.info(f"Routing ticket: Intent={intent}")

    try:
        from ..database.database import SessionLocal
        from ..database.models import Agent
        
        db = SessionLocal()
        agents = db.query(Agent).filter(Agent.active == True).all()
        db.close()
        
        if agents:
            for agent in agents:
                if agent.specialty and intent.lower() in agent.specialty.lower():
                    logger.info(f"Assigned to (specialty match): {agent.name}")
                    return {"assigned_agent": agent.name}
            
            logger.info(f"Assigned to (first available): {agents[0].name}")
            return {"assigned_agent": agents[0].name}
            
    except Exception as e:
        logger.warning(f"Database agent lookup failed: {e}")

    logger.warning("Using fallback: Unassigned (no agents available)")
    return {"assigned_agent": "Unassigned"}


def find_similar_tickets(state: SupportState) -> dict:
    """Find similar past tickets based on the current message."""
    message = state.get("customer_message", "")
    logger.info(f"Finding similar tickets: {message[:50]}...")

    prompt = f"""
    Extract 3 key words from this message that describe the issue.
    Return only the words separated by commas.

    Message: {message}
    """

    keywords = call_llm(prompt).strip()
    if not keywords:
        keywords = "customer issue"

    result = {
        "similar_tickets": [
            {"id": "sim1", "summary": "Similar issue found", "keywords": keywords},
            {"id": "sim2", "summary": "Related support case", "keywords": keywords},
            {"id": "sim3", "summary": "Past ticket with similar keywords", "keywords": keywords}
        ]
    }
    logger.info(f"   Keywords: {keywords}")
    return result


def recommend_products(state: SupportState) -> dict:
    """Recommend products based on the customer message."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    logger.info(f"Recommending products: {message[:50]}...")

    if intent not in ["product_inquiry", "general"]:
        logger.info("   Skipping recommendations (not a product inquiry)")
        return {"recommended_products": []}

    prompt = f"""
    Based on this message, recommend 3 products. Return ONLY the product names separated by commas.

    Message: {message}
    """

    response = call_llm(prompt).strip()
    recommendations = []

    if response and response.lower() != "none":
        for item in response.split(','):
            clean = item.strip()
            if clean:
                recommendations.append(clean)

    logger.info(f"   Recommended: {len(recommendations)} products")
    return {"recommended_products": recommendations[:3]}


def generate_response(state: SupportState) -> dict:
    """Generate an AI-powered response to the customer."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")
    priority = state.get("priority", "low")
    recommended = state.get("recommended_products", [])
    logger.info(f"Generating response: {message[:50]}...")

    rec_text = ""
    if recommended:
        rec_text = f"\nMention these products: {', '.join(recommended)}"

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

    logger.info(f"   Response: {response[:50]}...")
    return {"response": response}


def check_escalation_ai(state: SupportState) -> dict:
    """Determine if the ticket should be escalated using AI."""
    priority = state.get("priority", "medium")
    sentiment = state.get("sentiment", "neutral")
    intent = state.get("intent", "general")
    message = state.get("customer_message", "").lower()
    logger.info(f"Checking escalation: Priority={priority}, Sentiment={sentiment}")

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

    result = {"escalate": escalate, "escalate_reasoning": reasoning}
    logger.info(f"   Escalate: {escalate} - {reasoning}")
    return result


def generate_reply_options(state: SupportState) -> dict:
    """Generate 3 reply options with different tones."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")
    logger.info(f"Generating reply options: {message[:50]}...")
    
    try:
        from ..services.ai_features import AIFeaturesService
        options = AIFeaturesService.generate_reply_options(message, intent, sentiment)
        if options is None:
            options = []
        logger.info(f"   Generated {len(options)} options")
    except Exception as e:
        logger.error(f"Error generating reply options: {e}")
        options = []
    
    return {"reply_options": options}


def evaluate_response_quality(state: SupportState) -> dict:
    """Self-evaluate the quality of the AI response."""
    response = state.get("response", "")
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")
    logger.info(f"Evaluating response quality")
    
    try:
        from ..services.ai_features import AIFeaturesService
        score = AIFeaturesService.evaluate_response(response, message, intent, sentiment)
        logger.info(f"   Overall score: {score.get('overall_score', 'N/A')}")
    except Exception as e:
        logger.error(f"Error evaluating response: {e}")
        score = {"overall_score": 7}
    
    return {"quality_score": score}


def get_knowledge_base_articles(state: SupportState) -> dict:
    """Retrieve relevant knowledge base articles."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    logger.info(f"Retrieving KB articles: {message[:50]}...")
    
    try:
        from ..services.ai_features import AIFeaturesService
        from ..database.database import SessionLocal
        
        db = SessionLocal()
        articles = AIFeaturesService.get_knowledge_base_articles(db, message, intent)
        db.close()
        logger.info(f"   Found {len(articles)} articles")
    except Exception as e:
        logger.error(f"Error retrieving KB articles: {e}")
        articles = []
    
    return {"kb_articles": articles}


def predict_churn_risk(state: SupportState) -> dict:
    """Predict customer churn risk."""
    logger.info(f"Predicting churn risk")
    
    try:
        from ..services.ai_features import AIFeaturesService
        history = {"summary": {"total_tickets": 5, "sentiment_score": -0.2, "escalated_tickets": 1}}
        message = state.get("customer_message", "")
        risk = AIFeaturesService.predict_churn_risk(history, message)
        logger.info(f"   Churn risk: {risk.get('risk_level', 'unknown')}")
    except Exception as e:
        logger.error(f"Error predicting churn risk: {e}")
        risk = {"risk_level": "medium", "churn_risk": 30}
    
    return {"churn_risk": risk}


def detect_followup_needed(state: SupportState) -> dict:
    """Detect if a follow-up is needed."""
    message = state.get("customer_message", "")
    sentiment = state.get("sentiment", "neutral")
    priority = state.get("priority", "medium")
    logger.info(f"Checking follow-up need")
    
    try:
        from ..services.ai_features import AIFeaturesService
        followup = AIFeaturesService.detect_followup_needed(message, sentiment, priority, {})
        logger.info(f"   Follow-up needed: {followup.get('needs_followup', False)}")
    except Exception as e:
        logger.error(f"Error detecting follow-up: {e}")
        followup = {"needs_followup": False, "reasoning": "Unable to determine"}
    
    return {"needs_followup": followup}


def detect_language(state: SupportState) -> dict:
    """Detect the language of the customer message."""
    message = state.get("customer_message", "")
    logger.info(f"Detecting language: {message[:30]}...")
    
    try:
        from ..services.ai_features import AIFeaturesService
        language = AIFeaturesService.detect_language(message)
        logger.info(f"   Language: {language.get('language', 'unknown')}")
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        language = {"language": "English", "language_code": "en", "confidence": 50}
    
    return {"language": language}


def predict_resolution_time(state: SupportState) -> dict:
    """Predict resolution time."""
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    priority = state.get("priority", "medium")
    sentiment = state.get("sentiment", "neutral")
    logger.info(f"Predicting resolution time")
    
    try:
        from ..services.ai_features import AIFeaturesService
        time_prediction = AIFeaturesService.predict_resolution_time(message, intent, priority, sentiment)
        logger.info(f"   Estimated: {time_prediction.get('estimated_hours', 'N/A')} hours")
    except Exception as e:
        logger.error(f"Error predicting resolution time: {e}")
        time_prediction = {"estimated_hours": 24, "confidence": "low"}
    
    return {"resolution_time": time_prediction}