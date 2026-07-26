"""
Unit tests for the AI workflow.
Run: pytest tests/test_workflow.py -v
"""

import pytest
from app.workflow.workflow import process_message
from app.workflow.nodes import (
    classify_intent,
    analyze_sentiment,
    assign_priority_ai,
    generate_ticket_summary
)


class TestWorkflow:
    """Test the AI workflow nodes."""
    
    def test_classify_intent_refund(self):
        """Test intent classification for refund requests."""
        result = classify_intent({"customer_message": "I want my money back"})
        assert result["intent"] == "refund"
    
    def test_classify_intent_shipping(self):
        """Test intent classification for shipping inquiries."""
        result = classify_intent({"customer_message": "When will my order arrive?"})
        assert result["intent"] == "shipping"
    
    def test_classify_intent_product_inquiry(self):
        """Test intent classification for product inquiries."""
        result = classify_intent({"customer_message": "Which laptop do you recommend?"})
        assert result["intent"] == "product_inquiry"
    
    def test_classify_intent_complaint(self):
        """Test intent classification for complaints."""
        result = classify_intent({"customer_message": "This product is terrible"})
        assert result["intent"] == "complaint"
    
    def test_analyze_sentiment_positive(self):
        """Test sentiment analysis for positive messages."""
        result = analyze_sentiment({"customer_message": "I love this product!"})
        assert result["sentiment"] == "positive"
    
    def test_analyze_sentiment_negative(self):
        """Test sentiment analysis for negative messages."""
        result = analyze_sentiment({"customer_message": "This is awful"})
        assert result["sentiment"] == "negative"
    
    def test_analyze_sentiment_neutral(self):
        """Test sentiment analysis for neutral messages."""
        result = analyze_sentiment({"customer_message": "I have a question"})
        assert result["sentiment"] == "neutral"
    
    def test_assign_priority_urgent(self):
        """Test priority assignment for urgent messages."""
        result = assign_priority_ai({
            "customer_message": "URGENT: Need help immediately",
            "intent": "complaint",
            "sentiment": "negative"
        })
        # The priority could be 'urgent' or 'high' depending on the LLM response
        # Both are acceptable
        assert result["priority"] in ["urgent", "high"]
    
    def test_assign_priority_low(self):
        """Test priority assignment for low priority messages."""
        result = assign_priority_ai({
            "customer_message": "Do you have this in blue?",
            "intent": "product_inquiry",
            "sentiment": "neutral"
        })
        assert result["priority"] in ["low", "medium"]
    
    def test_process_message_complete(self):
        """Test the complete message processing workflow."""
        result = process_message("My laptop screen is cracked. I need help.")
        
        assert "intent" in result
        assert "sentiment" in result
        assert "priority" in result
        assert "response" in result
        assert "escalate" in result
    
    def test_process_message_returns_dict(self):
        """Test that process_message always returns a dict."""
        result = process_message("Hello")
        assert isinstance(result, dict)
        assert "customer_message" in result
        assert result["customer_message"] == "Hello"


class TestTicketCreation:
    """Test ticket creation flow."""
    
    def test_ticket_has_required_fields(self):
        """Test that tickets have all required AI fields."""
        result = process_message("My order hasn't arrived")
        
        required_fields = [
            "intent", "sentiment", "priority", 
            "response", "escalate", "ticket_summary"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing field: {field}"