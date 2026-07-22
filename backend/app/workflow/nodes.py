"""
Workflow node implementations for the customer support system.
Each node performs a specific task in the processing pipeline.
"""

from .state import SupportState
from .llm import call_llm


def classify_intent(state: SupportState) -> dict:
    """
    Classify the customer's intent using the LLM.

    Args:
        state: Current workflow state containing the customer message

    Returns:
        Dictionary with the classified intent
    """
    message = state.get("customer_message", "")

    prompt = f"""
    Classify this customer message into ONE category:
    - refund: Request for money back or return
    - shipping: Delivery, tracking, or shipping questions
    - product_inquiry: Questions about features, specs, or availability
    - complaint: Negative feedback about a product or service
    - general: Everything else

    Message: {message}

    Return only the category name.
    """

    intent = call_llm(prompt).strip().lower()
    valid_intents = ["refund", "shipping", "product_inquiry", "complaint", "general"]
    if intent not in valid_intents:
        intent = "general"

    return {"intent": intent}


def analyze_sentiment(state: SupportState) -> dict:
    """
    Analyze the sentiment of the customer message using the LLM.

    Args:
        state: Current workflow state

    Returns:
        Dictionary with the analyzed sentiment
    """
    message = state.get("customer_message", "")

    prompt = f"""
    Analyze the sentiment of this message.
    Choose one: positive, neutral, or negative.

    Message: {message}

    Return only the sentiment word.
    """

    sentiment = call_llm(prompt).strip().lower()
    valid_sentiments = ["positive", "neutral", "negative"]
    if sentiment not in valid_sentiments:
        sentiment = "neutral"

    return {"sentiment": sentiment}


def assign_priority(state: SupportState) -> dict:
    """
    Assign a priority level based on the intent and sentiment.

    Priority rules:
    - urgent: Negative sentiment with complaint or refund request
    - high: Negative sentiment or complaint/refund request
    - medium: Shipping inquiries
    - low: Everything else

    Args:
        state: Current workflow state

    Returns:
        Dictionary with the assigned priority
    """
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")

    if sentiment == "negative" and intent in ["complaint", "refund"]:
        priority = "urgent"
    elif sentiment == "negative":
        priority = "high"
    elif intent in ["complaint", "refund"]:
        priority = "high"
    elif intent == "shipping":
        priority = "medium"
    else:
        priority = "low"

    return {"priority": priority}


def recommend_products(state: SupportState) -> dict:
    """
    Recommend products based on the customer message.

    Args:
        state: Current workflow state

    Returns:
        Dictionary with recommended products list
    """
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")

    # Only recommend products for product inquiries or general questions
    if intent not in ["product_inquiry", "general"]:
        return {"recommended_products": []}

    prompt = f"""
    Based on this customer message, recommend 3 relevant products.
    Return ONLY a comma-separated list of product names.
    If no products are relevant, return "None".

    Message: {message}

    Example format: MacBook Pro, Dell XPS 15, Lenovo ThinkPad
    """

    response = call_llm(prompt)

    recommendations = []
    if response and response.strip().lower() != "none":
        # Split by comma and clean up
        for item in response.split(','):
            clean_item = item.strip()
            if clean_item:
                recommendations.append(clean_item)

    return {"recommended_products": recommendations[:3]}


def generate_response(state: SupportState) -> dict:
    """
    Generate an AI-powered response to the customer.

    Args:
        state: Current workflow state

    Returns:
        Dictionary with the generated response
    """
    message = state.get("customer_message", "")
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")
    priority = state.get("priority", "low")
    recommended_products = state.get("recommended_products", [])

    # Build prompt with recommendations if available
    recommendations_text = ""
    if recommended_products:
        recommendations_text = f"""
        Recommended products: {', '.join(recommended_products)}
        Consider mentioning these if relevant to the customer's inquiry.
        """

    prompt = f"""
    Write a customer support response.

    Customer message: {message}
    Intent: {intent}
    Sentiment: {sentiment}
    Priority: {priority}
    {recommendations_text}

    Requirements:
    - Be professional and empathetic
    - Address the specific concern
    - Provide clear next steps
    - Keep to 3-5 sentences
    - If sentiment is negative, start with an apology
    - If recommendations are provided, mention them naturally

    Return only the response text.
    """

    response = call_llm(prompt)
    return {"response": response}


def check_escalation(state: SupportState) -> dict:
    """
    Determine if the ticket should be escalated to a human agent.

    Escalation triggers:
    1. Priority is 'urgent'
    2. Negative sentiment with complaint intent
    3. Urgent keywords detected in the message

    Args:
        state: Current workflow state

    Returns:
        Dictionary with escalation decision and reasoning
    """
    intent = state.get("intent", "general")
    sentiment = state.get("sentiment", "neutral")
    priority = state.get("priority", "low")
    message = state.get("customer_message", "").lower()

    urgent_keywords = [
        "urgent", "immediately", "asap", "emergency",
        "furious", "terrible", "horrible", "disappointed"
    ]

    if priority == "urgent":
        return {"escalate": True, "reasoning": "Urgent priority requires human attention"}

    if sentiment == "negative" and intent == "complaint":
        return {"escalate": True, "reasoning": "Negative complaint may need human intervention"}

    if any(keyword in message for keyword in urgent_keywords):
        return {"escalate": True, "reasoning": "Urgent language detected in message"}

    return {"escalate": False, "reasoning": "Auto-response is sufficient"}