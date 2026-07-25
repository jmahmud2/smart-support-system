"""
State definition for the LangGraph customer support workflow.
Defines the data structure that flows through the workflow nodes.
"""

from typing import TypedDict, Optional, List


class SupportState(TypedDict):
    """
    Represents the state of a customer support ticket as it passes through the workflow.
    """
    customer_message: str
    intent: Optional[str]
    sentiment: Optional[str]
    sentiment_explanation: Optional[str]
    priority: Optional[str]
    priority_reasoning: Optional[str]
    response: Optional[str]
    escalate: bool
    escalate_reasoning: Optional[str]
    reasoning: Optional[str]
    product_id: Optional[int]
    recommended_products: Optional[List[str]]
    assigned_agent: Optional[str]
    ticket_summary: Optional[str]
    similar_tickets: Optional[List[dict]]
    reply_options: Optional[List[dict]]  # Smart Reply Optimization
    quality_score: Optional[dict]        # Quality Score
    kb_articles: Optional[List[dict]]    # Knowledge Base RAG
    churn_risk: Optional[dict]           # Churn Prediction
    needs_followup: Optional[dict]       # Auto-Follow-up
    language: Optional[dict]             # Multi-Language Detection
    resolution_time: Optional[dict]      # Resolution Time Prediction
    feedback_analysis: Optional[dict]    # Feedback Analysis