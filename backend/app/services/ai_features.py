"""
Advanced AI features service for customer support.
Includes smart reply, quality scoring, RAG, churn prediction, and more.
"""

import json
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from ..workflow.llm import call_llm
from ..database.models import SupportTicket, Product, KnowledgeBase
from .customer_context import CustomerContextService
from ..services.vector_db import VectorDatabase
from ..services.embeddings import EmbeddingService
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AIFeaturesService:
    """Advanced AI features for support tickets."""

    # ============ 1. SMART REPLY OPTIMIZATION ============
    
    @staticmethod
    def generate_reply_options(message: str, intent: str, sentiment: str) -> List[dict]:
        """Generate 3 reply options with different tones."""
        
        prompt = f"""
        Generate 3 customer support reply options for this message.
        
        Customer Message: {message}
        Intent: {intent}
        Sentiment: {sentiment}
        
        Return a JSON array with 3 objects:
        [
            {{
                "tone": "empathetic",
                "reply": "reply text here",
                "reasoning": "why this tone works"
            }},
            {{
                "tone": "direct_professional",
                "reply": "reply text here",
                "reasoning": "why this tone works"
            }},
            {{
                "tone": "detailed_informative",
                "reply": "reply text here",
                "reasoning": "why this tone works"
            }}
        ]
        
        Requirements:
        - Each reply should be 2-4 sentences
        - All replies should address the customer's concern
        - Each tone should be distinct
        """
        
        try:
            response = call_llm(prompt)
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            if response.startswith('```'):
                response = response.replace('```', '').strip()
            options = json.loads(response)
            return options[:3]
        except Exception as e:
            logger.error(f"Error generating reply options: {e}")
            return [
                {"tone": "empathetic", "reply": "I understand your frustration. Let me help resolve this right away.", "reasoning": "Shows empathy"},
                {"tone": "direct", "reply": "Here's what we can do to fix this issue. Let me explain the steps.", "reasoning": "Clear and direct"},
                {"tone": "detailed", "reply": "I've looked into this and here's a detailed breakdown of what happened and how we'll resolve it.", "reasoning": "Provides details"}
            ]

    # ============ 2. QUALITY SCORE ============
    
    @staticmethod
    def evaluate_response(response: str, message: str, intent: str, sentiment: str) -> dict:
        """Self-evaluate the quality of an AI-generated response."""
        
        prompt = f"""
        Evaluate this customer support response on quality metrics.
        
        Customer Message: {message}
        Intent: {intent}
        Sentiment: {sentiment}
        AI Response: {response}
        
        Return a JSON object:
        {{
            "clarity": 0-10,
            "empathy": 0-10,
            "completeness": 0-10,
            "tone_appropriateness": 0-10,
            "overall_score": 0-10,
            "strengths": ["list of strengths"],
            "improvements": ["list of improvements"],
            "recommendation": "brief recommendation"
        }}
        """
        
        try:
            response_text = call_llm(prompt)
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            if response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Error evaluating response: {e}")
            return {
                "clarity": 7,
                "empathy": 7,
                "completeness": 7,
                "tone_appropriateness": 7,
                "overall_score": 7,
                "strengths": ["Response is professional"],
                "improvements": ["Could be more personalized"],
                "recommendation": "Consider adding more empathy"
            }

    # ============ 3. KNOWLEDGE BASE RAG (WITH VECTOR SEARCH) ============
    
    @staticmethod
    def get_knowledge_base_articles_rag(db: Session, message: str, intent: str, n_results: int = 5) -> List[dict]:
        """
        Retrieve relevant knowledge base articles using RAG (vector search).
        
        Args:
            db: Database session
            message: Customer message
            intent: Intent category
            n_results: Number of results to return
        
        Returns:
            List of relevant articles with similarity scores
        """
        try:
            vector_db = VectorDatabase()
            
            # Search for similar articles
            results = vector_db.search(message, n_results=n_results)
            
            # Format results
            articles = []
            for result in results:
                metadata = result.get('metadata', {})
                articles.append({
                    'id': result.get('id'),
                    'title': metadata.get('title', 'Unknown'),
                    'content': result.get('content', ''),
                    'category': metadata.get('category', 'general'),
                    'tags': metadata.get('tags', ''),
                    'similarity': result.get('similarity', 0)
                })
            
            # If vector search returns nothing, fallback to category filtering
            if not articles:
                logger.warning("Vector search returned no results, falling back to category filter")
                fallback = db.query(KnowledgeBase).filter(
                    KnowledgeBase.category == intent
                ).limit(3).all()
                
                if not fallback:
                    fallback = db.query(KnowledgeBase).filter(
                        KnowledgeBase.category == "general"
                    ).limit(3).all()
                
                articles = [
                    {
                        'id': a.id,
                        'title': a.title,
                        'content': a.content,
                        'category': a.category,
                        'tags': a.tags,
                        'similarity': 0
                    }
                    for a in fallback
                ]
            
            return articles
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge base articles with RAG: {e}")
            return []

    # ============ 4. CHURN PREDICTION ============
    
    @staticmethod
    def predict_churn_risk(customer_history: dict, current_message: str) -> dict:
        """Predict customer churn risk based on history and current message."""
        
        total_tickets = customer_history.get('summary', {}).get('total_tickets', 0)
        sentiment_score = customer_history.get('summary', {}).get('sentiment_score', 0)
        escalated_count = customer_history.get('summary', {}).get('escalated_tickets', 0)
        
        prompt = f"""
        Predict customer churn risk based on this customer data.
        
        Customer Data:
        - Total Tickets: {total_tickets}
        - Sentiment Score: {sentiment_score} (-1 to 1)
        - Escalated Tickets: {escalated_count}
        - Current Message: {current_message}
        
        Return a JSON object:
        {{
            "churn_risk": 0-100,
            "risk_level": "low|medium|high|critical",
            "factors": ["list of contributing factors"],
            "recommendation": "what to do"
        }}
        """
        
        try:
            response = call_llm(prompt)
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            if response.startswith('```'):
                response = response.replace('```', '').strip()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error predicting churn risk: {e}")
            return {
                "churn_risk": 30,
                "risk_level": "medium",
                "factors": ["Multiple tickets", "Mixed sentiment"],
                "recommendation": "Follow up with the customer"
            }

    # ============ 5. AUTO-FOLLOW-UP DETECTION ============
    
    @staticmethod
    def detect_followup_needed(message: str, sentiment: str, priority: str, history: dict) -> dict:
        """Detect if a follow-up is needed after resolution."""
        
        prompt = f"""
        Determine if this ticket requires a follow-up after resolution.
        
        Message: {message}
        Sentiment: {sentiment}
        Priority: {priority}
        Customer History: {json.dumps(history.get('summary', {}), indent=2)}
        
        Return a JSON object:
        {{
            "needs_followup": true/false,
            "reasoning": "explanation",
            "suggested_timeline": "1 day|3 days|1 week",
            "followup_question": "suggested question for the customer"
        }}
        """
        
        try:
            response = call_llm(prompt)
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            if response.startswith('```'):
                response = response.replace('```', '').strip()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error detecting follow-up: {e}")
            return {
                "needs_followup": priority == "urgent" or sentiment == "negative",
                "reasoning": "Based on priority and sentiment",
                "suggested_timeline": "3 days",
                "followup_question": "How is everything working now?"
            }

    # ============ 6. MULTI-LANGUAGE DETECTION ============
    
    @staticmethod
    def detect_language(message: str) -> dict:
        """Detect the language of the customer message."""
        
        prompt = f"""
        Detect the language of this message.
        Return a JSON object:
        {{
            "language": "language name",
            "language_code": "en|es|fr|de|zh|ja|ar|other",
            "confidence": 0-100
        }}
        
        Message: {message}
        """
        
        try:
            response = call_llm(prompt)
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            if response.startswith('```'):
                response = response.replace('```', '').strip()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return {"language": "English", "language_code": "en", "confidence": 50}
    
    @staticmethod
    def translate_message(message: str, target_language: str = "English") -> str:
        """Translate message to target language."""
        
        prompt = f"""
        Translate this message to {target_language}.
        Return only the translation.
        
        Message: {message}
        """
        
        return call_llm(prompt)

    # ============ 7. RESOLUTION TIME PREDICTION ============
    
    @staticmethod
    def predict_resolution_time(message: str, intent: str, priority: str, sentiment: str) -> dict:
        """Predict how long it will take to resolve the ticket."""
        
        prompt = f"""
        Predict the resolution time for this ticket in hours.
        
        Message: {message}
        Intent: {intent}
        Priority: {priority}
        Sentiment: {sentiment}
        
        Return a JSON object:
        {{
            "estimated_hours": number,
            "minimum_hours": number,
            "maximum_hours": number,
            "confidence": "low|medium|high",
            "reasoning": "explanation"
        }}
        """
        
        try:
            response = call_llm(prompt)
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            if response.startswith('```'):
                response = response.replace('```', '').strip()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error predicting resolution time: {e}")
            base_hours = 2 if priority == "urgent" else 24 if priority == "high" else 48
            return {
                "estimated_hours": base_hours,
                "minimum_hours": base_hours * 0.5,
                "maximum_hours": base_hours * 2,
                "confidence": "low",
                "reasoning": "Based on priority level"
            }

    # ============ 8. CUSTOMER SENTIMENT TRENDS ============
    
    @staticmethod
    def analyze_sentiment_trends(customer_history: dict) -> dict:
        """Analyze customer sentiment trends over time."""
        
        tickets = customer_history.get('tickets', [])
        if not tickets:
            return {"trend": "stable", "message": "No enough data"}
        
        recent_tickets = tickets[:5]
        
        prompt = f"""
        Analyze this customer's sentiment trends over their last {len(recent_tickets)} tickets.
        
        Ticket History: {json.dumps(recent_tickets, indent=2)}
        
        Return a JSON object:
        {{
            "trend": "improving|declining|stable|volatile",
            "current_sentiment": "positive|neutral|negative",
            "previous_sentiment": "positive|neutral|negative",
            "change": "improved|worsened|same",
            "insight": "brief insight"
        }}
        """
        
        try:
            response = call_llm(prompt)
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            if response.startswith('```'):
                response = response.replace('```', '').strip()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error analyzing sentiment trends: {e}")
            return {
                "trend": "stable",
                "current_sentiment": "neutral",
                "previous_sentiment": "neutral",
                "change": "same",
                "insight": "Customer sentiment appears stable"
            }

    # ============ 9. FEEDBACK ANALYSIS ============
    
    @staticmethod
    def analyze_feedback(feedback: str, ticket_data: dict) -> dict:
        """Analyze post-resolution feedback from customers."""
        
        prompt = f"""
        Analyze this customer feedback after ticket resolution.
        
        Feedback: {feedback}
        Original Ticket Intent: {ticket_data.get('intent', 'unknown')}
        Priority: {ticket_data.get('priority', 'unknown')}
        
        Return a JSON object:
        {{
            "sentiment": "positive|neutral|negative",
            "key_themes": ["list of themes"],
            "satisfaction_score": 0-10,
            "suggestions": ["list of improvements"],
            "action_items": ["list of action items"]
        }}
        """
        
        try:
            response = call_llm(prompt)
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            if response.startswith('```'):
                response = response.replace('```', '').strip()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error analyzing feedback: {e}")
            return {
                "sentiment": "neutral",
                "key_themes": ["Resolution completed"],
                "satisfaction_score": 7,
                "suggestions": ["Consider faster response time"],
                "action_items": ["Monitor future tickets"]
            }