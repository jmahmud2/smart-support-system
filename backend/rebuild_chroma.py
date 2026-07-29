import os
from app.database.database import SessionLocal
from app.database.models import KnowledgeBase
from app.services.vector_db import VectorDatabase
from app.utils.logger import get_logger

logger = get_logger(__name__)

def rebuild_chroma():
    """Rebuild the ChromaDB vector database from knowledge base articles."""
    print("🔄 Starting ChromaDB rebuild...")
    
    db = SessionLocal()
    vector_db = VectorDatabase()
    
    try:
        # Clear existing collection
        vector_db.reset_collection()
        print("✅ Cleared existing collection")
        
        # Get all KB articles
        articles = db.query(KnowledgeBase).all()
        print(f"📚 Found {len(articles)} articles")
        
        if not articles:
            print("⚠️ No articles found in knowledge base.")
            return
        
        # Prepare documents for embedding
        documents = []
        for article in articles:
            documents.append({
                'id': f"kb_{article.id}",
                'content': f"{article.title}\n\n{article.content}",
                'metadata': {
                    'title': article.title,
                    'category': article.category,
                    'tags': article.tags,
                }
            })
        
        # Add to ChromaDB
        vector_db.add_documents(documents)
        print(f"✅ Rebuilt ChromaDB with {len(documents)} articles")
        
        # Verify
        stats = vector_db.get_collection_stats()
        print(f"📊 Collection stats: {stats}")
        
    except Exception as e:
        print(f"❌ Error rebuilding ChromaDB: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_chroma()