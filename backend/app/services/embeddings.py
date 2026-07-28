"""
Embedding service for generating vector embeddings using sentence-transformers.
"""

import os
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Model name - can be changed via environment variable
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers."""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def _load_model(self):
        """Load the sentence-transformer model."""
        if self._model is None:
            try:
                logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
                self._model = SentenceTransformer(EMBEDDING_MODEL)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        self._load_model()
        embedding = self._model.encode(text)
        return embedding.tolist()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        self._load_model()
        embeddings = self._model.encode(texts)
        return embeddings.tolist()
    
    def generate_embedding_numpy(self, text: str) -> np.ndarray:
        """Generate embedding as numpy array."""
        self._load_model()
        return self._model.encode(text)
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))