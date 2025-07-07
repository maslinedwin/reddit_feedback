import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import pandas as pd
from typing import List, Tuple
import hashlib
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGManager:
    """Manages embeddings with persistence and incremental updates"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', embeddings_dir: str = 'embeddings'):
        self.model_name = model_name
        self.embeddings_dir = embeddings_dir
        self.embeddings_file = os.path.join(embeddings_dir, 'embeddings.pkl')
        self.metadata_file = os.path.join(embeddings_dir, 'metadata.pkl')
        
        # Create embeddings directory if it doesn't exist
        os.makedirs(embeddings_dir, exist_ok=True)
        
        # Initialize model
        logger.info(f"Loading SentenceTransformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Load existing embeddings and metadata
        self.embeddings = None
        self.metadata = None
        self.df = None
        self._load_embeddings()
    
    def _load_embeddings(self):
        """Load existing embeddings and metadata from disk"""
        try:
            if os.path.exists(self.embeddings_file) and os.path.exists(self.metadata_file):
                logger.info("Loading existing embeddings from disk...")
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded {len(self.embeddings)} embeddings")
            else:
                logger.info("No existing embeddings found")
                self.embeddings = np.array([])
                self.metadata = {
                    'indexed_ids': set(),
                    'last_update': None,
                    'data_hash': None
                }
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            self.embeddings = np.array([])
            self.metadata = {
                'indexed_ids': set(),
                'last_update': None,
                'data_hash': None
            }
    
    def _save_embeddings(self):
        """Save embeddings and metadata to disk"""
        try:
            logger.info("Saving embeddings to disk...")
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            logger.info("Embeddings saved successfully")
        except Exception as e:
            logger.error(f"Error saving embeddings: {e}")
    
    def _get_data_hash(self, df: pd.DataFrame) -> str:
        """Generate a hash of the dataframe to detect changes"""
        # Use shape and sample of data to create hash
        hash_str = f"{df.shape}_{df.head(10).to_string()}_{df.tail(10).to_string()}"
        return hashlib.md5(hash_str.encode()).hexdigest()
    
    def update_embeddings(self, df: pd.DataFrame, force_refresh: bool = False):
        """Update embeddings for new or changed data"""
        if df.empty:
            logger.warning("Empty dataframe provided")
            return
        
        self.df = df
        current_hash = self._get_data_hash(df)
        
        # Check if we need to refresh all embeddings
        if force_refresh or current_hash != self.metadata.get('data_hash'):
            logger.info("Data has changed or force refresh requested. Rebuilding all embeddings...")
            self._build_all_embeddings()
        else:
            # Check for new entries
            new_ids = set(df['id'].values) - self.metadata['indexed_ids']
            if new_ids:
                logger.info(f"Found {len(new_ids)} new entries to index")
                self._build_incremental_embeddings(new_ids)
            else:
                logger.info("No new entries to index")
    
    def _build_all_embeddings(self):
        """Build embeddings for all entries"""
        if self.df is None or self.df.empty:
            return
        
        # Filter out entries with empty text
        valid_df = self.df[self.df['text'].notna() & (self.df['text'] != '')]
        
        if valid_df.empty:
            logger.warning("No valid text entries to encode")
            return
        
        logger.info(f"Encoding {len(valid_df)} texts...")
        texts = valid_df['text'].tolist()
        
        # Encode in batches for memory efficiency
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.model.encode(batch, show_progress_bar=True)
            all_embeddings.append(batch_embeddings)
        
        self.embeddings = np.vstack(all_embeddings)
        self.metadata = {
            'indexed_ids': set(valid_df['id'].values),
            'last_update': datetime.now(),
            'data_hash': self._get_data_hash(self.df),
            'valid_indices': valid_df.index.tolist()
        }
        
        self._save_embeddings()
        logger.info(f"Built and saved {len(self.embeddings)} embeddings")
    
    def _build_incremental_embeddings(self, new_ids: set):
        """Build embeddings only for new entries"""
        if self.df is None:
            return
        
        # Get new entries
        new_df = self.df[self.df['id'].isin(new_ids)]
        valid_new_df = new_df[new_df['text'].notna() & (new_df['text'] != '')]
        
        if valid_new_df.empty:
            logger.warning("No valid new entries to encode")
            return
        
        logger.info(f"Encoding {len(valid_new_df)} new texts...")
        new_texts = valid_new_df['text'].tolist()
        new_embeddings = self.model.encode(new_texts, show_progress_bar=True)
        
        # Append to existing embeddings
        if self.embeddings.size > 0:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])
        else:
            self.embeddings = new_embeddings
        
        # Update metadata
        self.metadata['indexed_ids'].update(valid_new_df['id'].values)
        self.metadata['last_update'] = datetime.now()
        self.metadata['data_hash'] = self._get_data_hash(self.df)
        
        # Update valid indices
        if 'valid_indices' in self.metadata:
            self.metadata['valid_indices'].extend(valid_new_df.index.tolist())
        else:
            self.metadata['valid_indices'] = valid_new_df.index.tolist()
        
        self._save_embeddings()
        logger.info(f"Added {len(new_embeddings)} new embeddings")
    
    def find_similar_documents(self, query: str, top_k: int = 5) -> List[str]:
        """Find similar documents using cosine similarity"""
        if self.embeddings is None or self.embeddings.size == 0:
            logger.warning("No embeddings available")
            return ["No documents indexed yet. Please run the scraper first."]
        
        if self.df is None:
            logger.error("No dataframe loaded")
            return ["Error: No data available"]
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarity
        cosine_scores = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # Get top k indices
        top_k_indices = np.argsort(cosine_scores)[-top_k:][::-1]
        
        # Map back to original dataframe indices
        valid_indices = self.metadata.get('valid_indices', [])
        results = []
        
        for idx in top_k_indices:
            if idx < len(valid_indices):
                df_idx = valid_indices[idx]
                if df_idx < len(self.df):
                    row = self.df.iloc[df_idx]
                    text = row['text']
                    score = cosine_scores[idx]
                    author = row.get('author', 'unknown')
                    post_type = row.get('type', 'unknown')
                    
                    # Add more context for better analysis
                    if score > 0.7:  # High relevance
                        results.append(f"[HIGH RELEVANCE - Score: {score:.3f}] {post_type.upper()} by u/{author}: {text}")
                    elif score > 0.5:  # Medium relevance
                        results.append(f"[Score: {score:.3f}] {post_type} by u/{author}: {text}")
                    else:  # Lower relevance
                        results.append(f"[Score: {score:.3f}] {text}")
        
        return results if results else ["No similar documents found"]
    
    def get_stats(self) -> dict:
        """Get statistics about the indexed data"""
        return {
            'total_embeddings': len(self.embeddings) if self.embeddings is not None else 0,
            'last_update': self.metadata.get('last_update', 'Never'),
            'indexed_ids': len(self.metadata.get('indexed_ids', set())),
            'model': self.model_name
        }