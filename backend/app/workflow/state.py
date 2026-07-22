"""
State definition for the LangGraph customer support workflow.
Defines the data structure that flows through the workflow nodes.
"""

from typing import List, TypedDict, Optional, List


class SupportState(TypedDict):
    """
    Represents the state of a customer support ticket as it passes through the workflow.

    Attributes:
        customer_message: The original message from the customer
        intent: Classified intent (refund, shipping, product_inquiry, complaint, general)
        sentiment: Analyzed sentiment (positive, neutral, negative)
        priority: Assigned priority (low, medium, high, urgent)
        response: AI-generated response to the customer
        escalate: Flag indicating if the ticket should be escalated to a human
        reasoning: Explanation for the escalation decision
        product_id: Optional reference to a related product
    """
    customer_message: str
    intent: Optional[str]
    sentiment: Optional[str]
    priority: Optional[str]
    response: Optional[str]
    escalate: bool
    reasoning: Optional[str]
    product_id: Optional[int]
    recommended_products: Optional[List[str]]