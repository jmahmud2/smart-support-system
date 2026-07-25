"""
LangGraph workflow definition for the customer support system.
Orchestrates the processing pipeline from message to response.
"""

from langgraph.graph import StateGraph, END
from .state import SupportState
from .nodes import (
    classify_intent,
    analyze_sentiment,
    assign_priority_ai,
    generate_ticket_summary,
    intelligent_routing,
    find_similar_tickets,
    recommend_products,
    generate_response,
    check_escalation_ai,
    generate_reply_options,
    evaluate_response_quality,
    get_knowledge_base_articles,
    predict_churn_risk,
    detect_followup_needed,
    detect_language,
    predict_resolution_time,
)


def build_graph():
    """
    Build and compile the LangGraph workflow with all AI features.
    """
    workflow = StateGraph(SupportState)

    # Core nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("assign_priority_ai", assign_priority_ai)
    workflow.add_node("generate_ticket_summary", generate_ticket_summary)
    workflow.add_node("intelligent_routing", intelligent_routing)
    workflow.add_node("find_similar_tickets", find_similar_tickets)
    workflow.add_node("recommend_products", recommend_products)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("check_escalation_ai", check_escalation_ai)
    
    # New AI feature nodes
    workflow.add_node("generate_reply_options", generate_reply_options)
    workflow.add_node("evaluate_response_quality", evaluate_response_quality)
    workflow.add_node("get_knowledge_base_articles", get_knowledge_base_articles)
    workflow.add_node("predict_churn_risk", predict_churn_risk)
    workflow.add_node("detect_followup_needed", detect_followup_needed)
    workflow.add_node("detect_language", detect_language)
    workflow.add_node("predict_resolution_time", predict_resolution_time)

    # Define the execution flow
    workflow.set_entry_point("classify_intent")
    workflow.add_edge("classify_intent", "analyze_sentiment")
    workflow.add_edge("analyze_sentiment", "assign_priority_ai")
    workflow.add_edge("assign_priority_ai", "generate_ticket_summary")
    workflow.add_edge("generate_ticket_summary", "intelligent_routing")
    workflow.add_edge("intelligent_routing", "find_similar_tickets")
    workflow.add_edge("find_similar_tickets", "recommend_products")
    workflow.add_edge("recommend_products", "generate_reply_options")
    workflow.add_edge("generate_reply_options", "detect_language")
    workflow.add_edge("detect_language", "predict_resolution_time")
    workflow.add_edge("predict_resolution_time", "predict_churn_risk")
    workflow.add_edge("predict_churn_risk", "detect_followup_needed")
    workflow.add_edge("detect_followup_needed", "get_knowledge_base_articles")
    workflow.add_edge("get_knowledge_base_articles", "generate_response")
    workflow.add_edge("generate_response", "evaluate_response_quality")
    workflow.add_edge("evaluate_response_quality", "check_escalation_ai")
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

    result = graph.invoke(initial_state)
    return result