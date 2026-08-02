"""
LangGraph workflow definition for the customer support system.
Orchestrates the processing pipeline from message to response.
"""

from langgraph.graph import StateGraph, END
from .state import SupportState
from .nodes import (
    analyze_message_comprehensive,
    intelligent_routing,
    find_similar_tickets,
    recommend_products,
    generate_response,
    check_escalation_ai,
)


def build_graph():
    """
    Build and compile the LangGraph workflow with combined LLM calls.
    """
    workflow = StateGraph(SupportState)

    # Core nodes
    workflow.add_node("analyze_comprehensive", analyze_message_comprehensive)
    workflow.add_node("intelligent_routing", intelligent_routing)
    workflow.add_node("find_similar_tickets", find_similar_tickets)
    workflow.add_node("recommend_products", recommend_products)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("check_escalation_ai", check_escalation_ai)

    # Define flow
    workflow.set_entry_point("analyze_comprehensive")
    workflow.add_edge("analyze_comprehensive", "intelligent_routing")
    workflow.add_edge("intelligent_routing", "find_similar_tickets")
    workflow.add_edge("find_similar_tickets", "recommend_products")
    workflow.add_edge("recommend_products", "generate_response")
    workflow.add_edge("generate_response", "check_escalation_ai")
    workflow.add_edge("check_escalation_ai", END)

    return workflow.compile()


def process_message(message: str) -> dict:
    """
    Process a customer message through the complete workflow.
    """
    graph = build_graph()

    initial_state = {
        "customer_message": message,
        "intent": None,
        "sentiment": None,
        "sentiment_explanation": None,
        "priority": None,
        "priority_reasoning": None,
        "response": None,
        "escalate": False,
        "escalate_reasoning": None,
        "reasoning": None,
        "product_id": None,
        "recommended_products": [],
        "assigned_agent": None,
        "ticket_summary": None,
        "similar_tickets": [],
        "reply_options": [],
        "quality_score": None,
        "kb_articles": [],
        "churn_risk": None,
        "needs_followup": None,
        "language": None,
        "resolution_time": None,
        "feedback_analysis": None,
    }

    config = {"recursion_limit": 50}
    result = graph.invoke(initial_state, config=config)
    return result