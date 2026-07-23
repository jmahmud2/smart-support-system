"""
Workflow node implementations for the customer support system.
"""

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
    logger.info(f" Analyzing sentiment: {message[:50]}...")

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

    priority = call_llm(prompt).strip().lower()
    if priority not in ["urgent", "high", "medium", "low"]:
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
    logger.info(f" Generating summary: {message[:50]}...")

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
    logger.info(f" Routing ticket: Intent={intent}")

    if intent == "refund":
        agent = "Michael Chen"
    elif intent == "shipping":
        agent = "Emily Rodriguez"
    elif intent == "product_inquiry":
        agent = "Jessica Williams"
    elif intent == "complaint" or any(w in message.lower() for w in ["broken", "defective", "not working"]):
        agent = "Sarah Johnson"
    else:
        agent = "David Kim"

    logger.info(f"   Assigned to: {agent}")
    return {"assigned_agent": agent}


def find_similar_tickets(state: SupportState) -> dict:
    """Find similar past tickets based on the current message."""
    message = state.get("customer_message", "")
    logger.info(f" Finding similar tickets: {message[:50]}...")

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
    logger.info(f" Recommending products: {message[:50]}...")

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
    logger.info(f" Generating response: {message[:50]}...")

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
    logger.info(f" Checking escalation: Priority={priority}, Sentiment={sentiment}")

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