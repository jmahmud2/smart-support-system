"""
LangGraph workflow definition for the customer support system.
Orchestrates the processing pipeline from message to response.
"""

from langgraph.graph import StateGraph, END
from .state import SupportState
from .nodes import (
    classify_intent,
    analyze_sentiment,
    assign_priority,
    generate_response,
    check_escalation,
    recommend_products,
)


def build_graph():
    """
    Build and compile the LangGraph workflow.

    The workflow follows this pipeline:
    1. classify_intent - Determine what the customer wants
    2. analyze_sentiment - Understand the customer's emotional state
    3. assign_priority - Set urgency level
    4. recommend_products - Suggest relevant products (optional)
    5. generate_response - Create an AI response
    6. check_escalation - Decide if a human should intervene

    Returns:
        A compiled LangGraph StateGraph ready for execution
    """
    workflow = StateGraph(SupportState)

    # Add processing nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("assign_priority", assign_priority)
    workflow.add_node("recommend_products", recommend_products)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("check_escalation", check_escalation)

    # Define the execution flow
    workflow.set_entry_point("classify_intent")
    workflow.add_edge("classify_intent", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "assign_priority")
    workflow.add_edge("assign_priority", "recommend_products")
    workflow.add_edge("recommend_products", "generate_response")
    workflow.add_edge("generate_response", "check_escalation")
    workflow.add_edge("check_escalation", END)

    # Compile the graph for execution
    return workflow.compile()


def process_message(message: str) -> dict:
    """
    Process a customer message through the complete workflow.

    Args:
        message: The customer's message text

    Returns:
        Complete state dictionary with all analysis results
    """
    graph = build_graph()

    # Initialize the state with the customer message
    initial_state = {
        "customer_message": message,
        "intent": None,
        "sentiment": None,
        "priority": None,
        "response": None,
        "escalate": False,
        "reasoning": None,
        "product_id": None,
        "recommended_products": [],
    }

    # Execute the workflow
    result = graph.invoke(initial_state)
    return result