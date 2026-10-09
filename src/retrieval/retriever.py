import os
import json

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    from src.retrieval.retriever_jaccard import RegulatoryRetriever as JaccardRetriever


class RegulatoryRetriever:
    def __init__(self, data_path="data/processed/regulations.json"):
        self.data_path = data_path
        self.clauses = []
        if not SKLEARN_AVAILABLE:
            self._fallback = JaccardRetriever(data_path=data_path)
            self.clauses = self._fallback.clauses
            return
        self._fallback = None
        self.vectorizer = None
        self.clause_vectors = None
        self._load_data()
        self._build_index()

    def _load_data(self):
        if not os.path.exists(self.data_path):
            from src.ingestion.extract_regulations import extract_and_save_regulations
            self.clauses = extract_and_save_regulations(self.data_path)
        else:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.clauses = json.load(f)

    def _build_index(self):
        """
        Build a TF-IDF representation of the regulatory clauses.
        """
        documents = [
            (clause["title"] + " " + clause["text"]).lower()
            for clause in self.clauses
        ]

        self.vectorizer = TfidfVectorizer()
        self.clause_vectors = self.vectorizer.fit_transform(documents)

    def retrieve(self, query, top_k=2):
        """
        Retrieve the most relevant regulatory clauses.
        """
        if self._fallback is not None:
            return self._fallback.retrieve(query, top_k=top_k)

        query_vector = self.vectorizer.transform([query.lower()])
        similarity_scores = cosine_similarity(
            query_vector,
            self.clause_vectors
        )[0]

        ranked_indices = np.argsort(similarity_scores)[::-1][:top_k]

        results = [
            self.clauses[index]
            for index in ranked_indices
        ]

        return results


if __name__ == "__main__":
    retriever = RegulatoryRetriever()
    results = retriever.retrieve("insider trading earnings disclosure")

    print(
        "Retrieved top clause:",
        results[0]["title"] if results else "None"
    )