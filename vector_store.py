import numpy as np
from typing import List, Dict

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.encoder = None
        self.index = None
        self.metadata: List[Dict[str, any]] = []
        self._init_encoder(model_name)

    def _init_encoder(self, model_name: str):
        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            self.encoder = SentenceTransformer(model_name)
            dimension = self.encoder.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatIP(dimension)
        except Exception as e:
            print(f"Info: VectorStore local encoder initialization deferred ({e}).")

    def add_documents(self, chunks: List[Dict[str, any]]):
        """Encodes document chunks, normalizes, and adds to FAISS index."""
        if not chunks:
            return

        self.metadata.extend(chunks)

        if self.encoder is not None and self.index is not None:
            import faiss
            texts = [item["chunk"] for item in chunks]
            embeddings = self.encoder.encode(texts, convert_to_numpy=True)
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, any]]:
        """Searches FAISS vector index for query matches."""
        if self.index is not None and self.index.ntotal > 0:
            import faiss
            query_vector = self.encoder.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_vector)
            distances, indices = self.index.search(query_vector, min(top_k, self.index.ntotal))

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx != -1 and idx < len(self.metadata):
                    item = self.metadata[idx].copy()
                    item["score"] = float(dist)
                    results.append(item)
            return results
        
        # Fallback keyword match if FAISS isn't initialized
        query_words = set(query.lower().split())
        scored = []
        for item in self.metadata:
            text = item["chunk"].lower()
            score = sum(1 for w in query_words if w in text) / max(len(query_words), 1)
            scored.append((score, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [dict(s[1], score=round(s[0], 2)) for s in scored[:top_k]]

    def clear(self):
        """Resets the vector index and metadata."""
        if self.index is not None:
            self.index.reset()
        self.metadata = []
