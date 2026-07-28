"""
Seed knowledge base articles into the database and vector store with RAG.
Run: python scripts/seed_knowledge_base_with_rag.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.database import SessionLocal
from app.database.models import KnowledgeBase
from app.services.vector_db import VectorDatabase
from app.utils.logger import get_logger

logger = get_logger(__name__)

def seed_knowledge_base():
    db = SessionLocal()
    vector_db = VectorDatabase()
    
    try:
        # Clear existing articles
        db.query(KnowledgeBase).delete()
        db.commit()
        
        articles = [
            {
                "title": "How to Request a Refund",
                "content": "To request a refund, please follow these steps: 1. Log in to your account. 2. Go to Order History. 3. Select the order you want to refund. 4. Click 'Request Refund'. 5. Provide a reason. 6. Submit. Refunds are processed within 3-5 business days.",
                "category": "refund",
                "tags": "refund, return, money back, reimbursement"
            },
            {
                "title": "Return Policy",
                "content": "We accept returns within 30 days of purchase. Items must be in original condition with all packaging. To initiate a return, contact support with your order number and reason for return. Return shipping is free for defective items.",
                "category": "refund",
                "tags": "return, policy, refund, exchange"
            },
            {
                "title": "Tracking Your Order",
                "content": "To track your order: 1. Log in to your account. 2. Go to Order History. 3. Click 'Track Order' on your recent order. 4. You'll see real-time shipping updates. If you haven't received tracking within 48 hours, contact support.",
                "category": "shipping",
                "tags": "tracking, shipping, delivery, order status"
            },
            {
                "title": "Shipping Times and Methods",
                "content": "We offer standard (3-5 business days) and expedited (1-2 business days) shipping. International shipping takes 7-14 business days. All orders ship within 24 hours of confirmation. Tracking numbers are provided via email.",
                "category": "shipping",
                "tags": "shipping, delivery, expedited, international"
            },
            {
                "title": "Product Specifications Guide",
                "content": "Product specifications vary by item. For detailed specs, please check the product page. Key details include dimensions, weight, color options, material, and compatibility. Contact support for specific questions.",
                "category": "product_inquiry",
                "tags": "specifications, product details, features"
            },
            {
                "title": "Warranty Information",
                "content": "All products come with a standard 2-year warranty. The warranty covers manufacturing defects and malfunctions. It does not cover accidental damage or normal wear and tear. Register your product online to activate warranty.",
                "category": "complaint",
                "tags": "warranty, defect, malfunction, repair"
            },
            {
                "title": "Reporting a Complaint",
                "content": "To file a complaint: 1. Contact support with your order number. 2. Describe the issue in detail. 3. Attach any relevant photos. 4. Our team will investigate and respond within 24 hours. We take all complaints seriously.",
                "category": "complaint",
                "tags": "complaint, issue, problem, dissatisfied"
            },
            {
                "title": "General Support FAQs",
                "content": "Common questions: How to create an account, how to reset password, how to update payment method, how to cancel an order, how to contact support. Visit our FAQ page or contact support for specific questions.",
                "category": "general",
                "tags": "general, faq, account, support"
            }
        ]
        
        # Save to database first
        for article_data in articles:
            article = KnowledgeBase(**article_data)
            db.add(article)
            print(f"Added article to DB: {article_data['title']} ({article_data['category']})")
        
        db.commit()
        print("Articles added to database!")
        
        # Then add to vector database
        print("Adding articles to vector database...")
        
        # Reset vector collection
        vector_db.reset_collection()
        
        # Get all articles from DB
        db_articles = db.query(KnowledgeBase).all()
        
        documents = []
        for article in db_articles:
            documents.append({
                'id': str(article.id),
                'content': article.content,
                'metadata': {
                    'title': article.title,
                    'category': article.category,
                    'tags': article.tags
                }
            })
        
        added = vector_db.add_documents(documents)
        print(f"Added {added} documents to vector database")
        
        stats = vector_db.get_collection_stats()
        print(f"Vector database stats: {stats}")
        
        print("Knowledge base seeded successfully with RAG!")
        
    except Exception as e:
        print(f"Error seeding knowledge base: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_knowledge_base()