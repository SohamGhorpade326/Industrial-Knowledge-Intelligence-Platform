import os
from typing import List, Optional
from backend.app.core.config import get_settings
from backend.app.core.logging_config import logger

settings = get_settings()

_model = None
_chroma_client = None
_collection = None


def _init_embedding_model():
    global _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"Embedding model loaded: {settings.EMBEDDING_MODEL}")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        _model = None


def _init_chromadb():
    global _chroma_client, _collection
    try:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        _collection = _chroma_client.get_or_create_collection(
            name="industrial_knowledge",
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB initialized at {settings.CHROMA_DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize ChromaDB: {e}")
        _chroma_client = None
        _collection = None


class EmbeddingService:
    def __init__(self):
        if _model is None:
            _init_embedding_model()
        if _chroma_client is None:
            _init_chromadb()

    @property
    def is_available(self) -> bool:
        return _model is not None and _collection is not None

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        if _model is None:
            logger.warning("Embedding model not available")
            return []
        try:
            embeddings = _model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    def generate_single_embedding(self, text: str) -> List[float]:
        results = self.generate_embeddings([text])
        return results[0] if results else []

    def store_chunks(
        self,
        document_id: int,
        chunks: List[dict],
        filename: str,
        category: str = "",
        machine_name: str = "",
    ) -> int:
        if not self.is_available:
            logger.warning("Embedding service not available for storing chunks")
            return 0

        try:
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.generate_embeddings(texts)

            if not embeddings:
                return 0

            ids = []
            metadatas = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"doc_{document_id}_chunk_{i}"
                ids.append(chunk_id)
                metadatas.append({
                    "document_id": document_id,
                    "filename": filename,
                    "category": category,
                    "machine_name": machine_name,
                    "chunk_index": i,
                    "word_start": chunk.get("word_start", 0),
                    "word_end": chunk.get("word_end", 0),
                })

            _collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
            )

            logger.info(f"Stored {len(ids)} chunks for document {document_id}")
            return len(ids)
        except Exception as e:
            logger.error(f"Failed to store chunks: {e}")
            return 0

    def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[dict] = None,
    ) -> List[dict]:
        if not self.is_available:
            logger.warning("Embedding service not available for search")
            return []

        try:
            query_embedding = self.generate_single_embedding(query)
            if not query_embedding:
                return []

            search_params = {
                "query_embeddings": [query_embedding],
                "n_results": top_k,
            }
            if filter_metadata:
                search_params["where"] = filter_metadata

            results = _collection.query(**search_params)

            search_results = []
            if results and results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    search_results.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else 0.0,
                        "relevance_score": 1.0 - (results["distances"][0][i] if results["distances"] else 0.0),
                    })

            return search_results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    def delete_document_chunks(self, document_id: int) -> bool:
        if not self.is_available:
            return False
        try:
            _collection.delete(where={"document_id": document_id})
            logger.info(f"Deleted chunks for document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {e}")
            return False

    def get_collection_stats(self) -> dict:
        if not self.is_available:
            return {"count": 0, "available": False}
        try:
            count = _collection.count()
            return {"count": count, "available": True}
        except Exception:
            return {"count": 0, "available": False}


embedding_service = EmbeddingService()
