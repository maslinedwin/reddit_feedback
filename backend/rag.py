from rag_manager import RAGManager
from database import get_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize RAG manager
rag_manager = RAGManager()

# Load and index data on startup
logger.info("Initializing RAG system...")
df = get_data()
if not df.empty:
    rag_manager.update_embeddings(df)
    logger.info("RAG system initialized with existing data")
else:
    logger.info("No data found. RAG system initialized empty")

def find_similar_documents(query: str, top_k: int = 10):
    """Find similar documents using the RAG manager"""
    return rag_manager.find_similar_documents(query, top_k)

def update_rag_index():
    """Update the RAG index with latest data"""
    df = get_data()
    if not df.empty:
        rag_manager.update_embeddings(df)
        return True
    return False

def get_rag_stats():
    """Get statistics about the RAG system"""
    return rag_manager.get_stats()