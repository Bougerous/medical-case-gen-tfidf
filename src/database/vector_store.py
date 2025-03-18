"""Simple Vector Database module using scikit-learn for storing and retrieving knowledge."""
import os
import glob
import pickle
from typing import List, Dict
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from loguru import logger

from src.config import DOCS_DIR, DB_DIR, CHROMA_COLLECTION_NAME


class VectorStore:
    """Vector database for storing and retrieving medical knowledge using TF-IDF."""
    
    def __init__(self):
        """Initialize the vector store with TF-IDF."""
        # Create DB directory if it doesn't exist
        os.makedirs(DB_DIR, exist_ok=True)
        
        self.collection_name = CHROMA_COLLECTION_NAME
        self.vectorizer_path = os.path.join(
            DB_DIR, f"{self.collection_name}_vectorizer.pkl")
        self.documents_path = os.path.join(
            DB_DIR, f"{self.collection_name}_documents.json")
        self.vectors_path = os.path.join(
            DB_DIR, f"{self.collection_name}_vectors.npy")
        
        # Initialize or load existing data
        if (os.path.exists(self.vectorizer_path) and 
                os.path.exists(self.documents_path) and 
                os.path.exists(self.vectors_path)):
            self.load_model()
            logger.info(f"Loaded existing TF-IDF model: {self.collection_name}")
        else:
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.document_data = []
            self.vectors = None
            logger.info(f"Created new TF-IDF model: {self.collection_name}")
    
    def load_model(self):
        """Load the TF-IDF model and document data from disk."""
        try:
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(self.documents_path, 'r', encoding='utf-8') as f:
                self.document_data = json.load(f)
            
            self.vectors = np.load(self.vectors_path)
            logger.info(f"Loaded {len(self.document_data)} documents from disk")
        except Exception as e:
            logger.error(f"Error loading model from disk: {e}")
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.document_data = []
            self.vectors = None
    
    def save_model(self):
        """Save the TF-IDF model and document data to disk."""
        try:
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            with open(self.documents_path, 'w', encoding='utf-8') as f:
                json.dump(self.document_data, f)
            
            if self.vectors is not None:
                np.save(self.vectors_path, self.vectors)
            
            logger.info(f"Saved {len(self.document_data)} documents to disk")
        except Exception as e:
            logger.error(f"Error saving model to disk: {e}")
    
    def load_documents(self, force_reload: bool = False) -> None:
        """
        Load documents from the docs directory into the vector store.
        
        Args:
            force_reload: If True, clear the collection and reload all documents.
        """
        if not force_reload and self.count() > 0:
            logger.info(
                f"Collection already contains {self.count()} documents. Skipping loading.")
            return
        
        # Reset if force reload
        if force_reload:
            logger.info("Force reloading documents...")
            self.document_data = []
            self.vectors = None
        
        # Get all chunk files
        chunk_files = glob.glob(os.path.join(DOCS_DIR, "me_chunk_*.txt"))
        logger.info(f"Found {len(chunk_files)} chunk files to load")
        
        documents = []
        document_data = []
        
        for file_path in chunk_files:
            file_id = os.path.basename(file_path).replace(".txt", "")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:  # Only add non-empty documents
                    documents.append(content)
                    document_data.append({
                        "id": file_id,
                        "content": content,
                        "metadata": {"source": file_path}
                    })
            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
        
        if documents:
            # Fit and transform the documents
            self.vectors = self.vectorizer.fit_transform(documents)
            self.document_data = document_data
            
            # Save the model and data
            self.save_model()
            
            logger.info(f"Loaded {len(documents)} documents into vector store")
        else:
            logger.warning("No documents were loaded")
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """
        Query the vector store for relevant medical knowledge.
        
        Args:
            query_text: The query text.
            n_results: Number of results to return.
            
        Returns:
            List of dictionaries containing document content and metadata.
        """
        if not self.document_data or self.vectors is None:
            logger.warning("Vector store is empty, returning empty results")
            return []
        
        try:
            # Transform the query using the vectorizer
            query_vector = self.vectorizer.transform([query_text])
            
            # Calculate cosine similarity between query and all documents
            similarities = cosine_similarity(
                query_vector, self.vectors).flatten()
            
            # Get the indices of the top n_results
            top_indices = similarities.argsort()[-n_results:][::-1]
            
            # Create result list
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include if similarity is positive
                    doc = self.document_data[idx]
                    results.append({
                        'content': doc['content'],
                        'metadata': doc['metadata'],
                        'id': doc['id'],
                        'similarity': float(similarities[idx])
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
    
    def count(self) -> int:
        """Return the number of documents in the vector store."""
        return len(self.document_data) if hasattr(self, 'document_data') else 0
    
    def get_status(self) -> Dict:
        """Get the status of the vector store."""
        return {
            "collection_name": self.collection_name,
            "document_count": self.count(),
            "embedding_model": "scikit-learn TF-IDF"
        }