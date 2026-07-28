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
            # ============ REFUNDS ============
            {
                "title": "How to Request a Refund",
                "content": "To request a refund, please follow these steps: 1. Log in to your account. 2. Go to Order History. 3. Select the order you want to refund. 4. Click 'Request Refund'. 5. Provide a reason. 6. Submit. Refunds are processed within 3-5 business days.",
                "category": "refund",
                "tags": "refund, return, money back, reimbursement, refund process"
            },
            {
                "title": "Refund Policy and Timeline",
                "content": "Refunds are processed within 3-5 business days after approval. The refund will be credited to your original payment method. You will receive a confirmation email once the refund is initiated. If you don't see the refund after 5 business days, contact your bank.",
                "category": "refund",
                "tags": "refund, timeline, processing, bank, payment method"
            },
            {
                "title": "Partial Refund Eligibility",
                "content": "Partial refunds are available for damaged items, missing accessories, or if you decide to keep part of your order. To request a partial refund, contact support with your order number and specify which items you wish to keep and which you want refunded.",
                "category": "refund",
                "tags": "partial refund, damaged items, missing parts, keep items"
            },
            
            # ============ SHIPPING ============
            {
                "title": "Tracking Your Order",
                "content": "To track your order: 1. Log in to your account. 2. Go to Order History. 3. Click 'Track Order' on your recent order. 4. You'll see real-time shipping updates. If you haven't received tracking within 48 hours, contact support.",
                "category": "shipping",
                "tags": "tracking, shipping, delivery, order status, track order"
            },
            {
                "title": "Shipping Times and Methods",
                "content": "We offer standard (3-5 business days) and expedited (1-2 business days) shipping. International shipping takes 7-14 business days. All orders ship within 24 hours of confirmation. Tracking numbers are provided via email.",
                "category": "shipping",
                "tags": "shipping, delivery, expedited, international, standard shipping"
            },
            {
                "title": "International Shipping Information",
                "content": "International shipping is available to over 100 countries. Delivery times vary by destination (7-14 business days). Customs fees and import duties are the responsibility of the customer. Please check your country's import regulations before ordering.",
                "category": "shipping",
                "tags": "international shipping, customs, duties, global delivery, import taxes"
            },
            {
                "title": "Shipping Address Change",
                "content": "To change your shipping address after placing an order: 1. Contact support immediately with your order number and new address. 2. Address changes are only possible before the order is shipped. Once shipped, you'll need to redirect the package through the carrier.",
                "category": "shipping",
                "tags": "address change, shipping address, delivery address, change order"
            },
            
            # ============ PRODUCT INQUIRIES ============
            {
                "title": "Product Specifications Guide",
                "content": "Product specifications vary by item. For detailed specs, please check the product page. Key details include dimensions, weight, color options, material, and compatibility. Contact support for specific questions.",
                "category": "product_inquiry",
                "tags": "specifications, product details, features, dimensions, weight"
            },
            {
                "title": "Product Compatibility Check",
                "content": "To check if a product is compatible with your device: 1. Look for the compatibility section on the product page. 2. Check the model numbers and specifications listed. 3. If unsure, contact support with your device model number for assistance.",
                "category": "product_inquiry",
                "tags": "compatibility, compatible devices, model numbers, technical specs"
            },
            {
                "title": "Product Availability and Restocking",
                "content": "Products show 'In Stock' when available. If out of stock, you can sign up for email notifications. Restocking typically takes 1-2 weeks. For bulk orders, contact support for special arrangements and estimated delivery dates.",
                "category": "product_inquiry",
                "tags": "availability, stock, restock, backorder, bulk orders"
            },
            {
                "title": "Product Warranty and Guarantee",
                "content": "All products come with a 2-year manufacturer warranty against defects. If your product fails within the warranty period, contact support with proof of purchase. Extended warranties are available for select products.",
                "category": "product_inquiry",
                "tags": "warranty, guarantee, defect, replacement, extended warranty"
            },
            {
                "title": "Product Care and Maintenance",
                "content": "For electronics, keep away from moisture and extreme temperatures. For clothing, follow the care label instructions. For accessories, clean with a soft, dry cloth. Refer to the user manual for detailed care instructions.",
                "category": "product_inquiry",
                "tags": "care, maintenance, cleaning, user manual, product care"
            },
            
            # ============ COMPLAINTS ============
            {
                "title": "Warranty Information",
                "content": "All products come with a standard 2-year warranty. The warranty covers manufacturing defects and malfunctions. It does not cover accidental damage or normal wear and tear. Register your product online to activate warranty.",
                "category": "complaint",
                "tags": "warranty, defect, malfunction, repair, warranty claim"
            },
            {
                "title": "Reporting a Complaint",
                "content": "To file a complaint: 1. Contact support with your order number. 2. Describe the issue in detail. 3. Attach any relevant photos. 4. Our team will investigate and respond within 24 hours. We take all complaints seriously.",
                "category": "complaint",
                "tags": "complaint, issue, problem, dissatisfied, report issue"
            },
            {
                "title": "Defective Product Process",
                "content": "If you receive a defective product: 1. Do not use the product further. 2. Contact support within 7 days of delivery. 3. Provide your order number and describe the defect. 4. We will arrange a replacement or refund. 5. Return shipping is free for defective items.",
                "category": "complaint",
                "tags": "defective, broken, damaged, not working, faulty"
            },
            {
                "title": "Wrong Item Received",
                "content": "If you received the wrong item: 1. Do not open the packaging if possible. 2. Contact support with your order number and a photo of the received item. 3. We will arrange a return and ship the correct item within 24 hours. 4. You will not be charged for the return shipping.",
                "category": "complaint",
                "tags": "wrong item, incorrect order, wrong product, wrong size"
            },
            
            # ============ GENERAL ============
            {
                "title": "General Support FAQs",
                "content": "Common questions: How to create an account, how to reset password, how to update payment method, how to cancel an order, how to contact support. Visit our FAQ page or contact support for specific questions.",
                "category": "general",
                "tags": "general, faq, account, support, password reset"
            },
            {
                "title": "Account and Login Issues",
                "content": "If you're having trouble logging in: 1. Reset your password using the 'Forgot Password' link. 2. Check your email for the reset link. 3. If still issues, clear your browser cache or try a different browser. 4. Contact support if problems persist.",
                "category": "general",
                "tags": "account, login, password, forgot password, access"
            },
            {
                "title": "Payment and Billing Questions",
                "content": "We accept major credit cards, PayPal, and Apple Pay. Billing issues: 1. Check your payment method is valid. 2. Ensure you have sufficient funds. 3. If a charge appears twice, contact support. 4. Receipts are sent via email after each purchase.",
                "category": "general",
                "tags": "payment, billing, credit card, PayPal, receipt"
            },
            {
                "title": "Order Cancellation Policy",
                "content": "Orders can be canceled within 1 hour of placement. After that, they enter processing and may not be cancellable. If your order has already shipped, you'll need to process a return. Contact support immediately to request cancellation.",
                "category": "general",
                "tags": "cancel order, cancellation, order modification, cancel request"
            },
            {
                "title": "How to Contact Support",
                "content": "Contact support via: 1. Email: support@smart-support.com (Response within 24 hours). 2. Live Chat: Available 9 AM - 9 PM EST. 3. Phone: Available for urgent issues only. 4. Social Media: DM us on Twitter or Facebook for quick responses.",
                "category": "general",
                "tags": "contact, support, email, chat, phone, social media"
            },
            {
                "title": "Gift Wrapping and Special Requests",
                "content": "Gift wrapping is available for selected products. Add a gift message during checkout. For special requests (custom engraving, personalized messages), contact support before placing your order. Additional fees may apply.",
                "category": "general",
                "tags": "gift wrapping, special request, gift message, personalized, custom order"
            }
        ]
        
        # Save to database first
        print(f"Adding {len(articles)} articles to database...")
        for article_data in articles:
            article = KnowledgeBase(**article_data)
            db.add(article)
        
        db.commit()
        print(f"Added {len(articles)} articles to database!")
        
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
        
        print(f"Knowledge base seeded successfully with RAG! ({len(articles)} articles)")
        
        # Print summary by category
        category_count = {}
        for article in db_articles:
            category_count[article.category] = category_count.get(article.category, 0) + 1
        
        print("\nArticles by category:")
        for category, count in category_count.items():
            print(f"  - {category}: {count} articles")
        
    except Exception as e:
        print(f"Error seeding knowledge base: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_knowledge_base()