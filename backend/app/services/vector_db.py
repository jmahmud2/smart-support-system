"""
Vector database service using ChromaDB for semantic search.
"""

import os
import uuid
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from ..utils.logger import get_logger
from .embeddings import EmbeddingService
from ..database.models import KnowledgeBase

logger = get_logger(__name__)

# ChromaDB configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "knowledge_base")


class VectorDatabase:
    """ChromaDB wrapper for storing and retrieving knowledge base articles."""
    
    _instance = None
    _client = None
    _collection = None
    _embedding_service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDatabase, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._embedding_service = EmbeddingService()
        self._initialize_chroma()
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            # Ensure persist directory exists
            os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
            
            # Initialize client with persistence
            self._client = chromadb.PersistentClient(
                path=CHROMA_PERSIST_DIR,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self._collection = self._client.get_or_create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"ChromaDB initialized with collection: {COLLECTION_NAME}")
            logger.info(f"Collection has {self._collection.count()} documents")
            
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts using the embedding service."""
        return self._embedding_service.generate_embeddings(texts)
    
    def add_documents(self, documents: List[Dict]) -> int:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of dicts with keys: id, content, metadata
        
        Returns:
            Number of documents added
        """
        if not documents:
            return 0
        
        try:
            ids = []
            contents = []
            metadatas = []
            
            for doc in documents:
                doc_id = doc.get('id', str(uuid.uuid4()))
                content = doc.get('content', '')
                
                if not content:
                    continue
                
                ids.append(str(doc_id))
                contents.append(content)
                metadatas.append(doc.get('metadata', {}))
            
            if not ids:
                return 0
            
            # Generate embeddings in batch
            embeddings = self.get_embeddings(contents)
            
            # Add to ChromaDB
            self._collection.add(
                ids=ids,
                documents=contents,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(ids)} documents to vector database")
            return len(ids)
            
        except Exception as e:
            logger.error(f"Error adding documents to vector database: {e}")
            raise
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Search for similar documents in the vector database.
        
        Args:
            query: Search query text
            n_results: Number of results to return
        
        Returns:
            List of documents with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self._embedding_service.generate_embedding(query)
            
            # Search ChromaDB
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            documents = []
            if results and results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    doc = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i] if results['documents'] else '',
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'similarity': 1 - results['distances'][0][i] if results['distances'] else 0
                    }
                    documents.append(doc)
            
            logger.info(f"Found {len(documents)} relevant documents for query: {query[:50]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching vector database: {e}")
            return []
    
    def get_collection_stats(self) -> dict:
        """Get statistics about the collection."""
        return {
            "collection_name": COLLECTION_NAME,
            "document_count": self._collection.count(),
            "persist_directory": CHROMA_PERSIST_DIR
        }
    
    def reset_collection(self):
        """Reset the collection (delete all documents)."""
        try:
            self._client.delete_collection(COLLECTION_NAME)
            self._collection = self._client.create_collection(
                name=COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection {COLLECTION_NAME} has been reset")
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            raise