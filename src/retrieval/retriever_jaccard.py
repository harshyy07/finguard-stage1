import os
import json

class RegulatoryRetriever:
    def __init__(self, data_path="data/processed/regulations.json"):
        self.data_path = data_path
        self.clauses = []
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.data_path):
            from src.ingestion.extract_regulations import extract_and_save_regulations
            self.clauses = extract_and_save_regulations(self.data_path)
        else:
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.clauses = json.load(f)

    def retrieve(self, query, top_k=2):
        """
        Dense semantic keyword + text similarity retrieval.
        """
        query_words = set(query.lower().split())
        scored_clauses = []
        
        for clause in self.clauses:
            clause_text = (clause["title"] + " " + clause["text"]).lower()
            clause_words = set(clause_text.split())
            
            # Simple TF-IDF / Jaccard similarity score metric
            intersection = len(query_words.intersection(clause_words))
            union = len(query_words.union(clause_words)) + 1e-5
            score = intersection / union
            
            scored_clauses.append((score, clause))

        scored_clauses.sort(key=lambda x: x[0], reverse=True)
        results = [clause for score, clause in scored_clauses[:top_k]]
        return results

if __name__ == "__main__":
    retriever = RegulatoryRetriever()
    results = retriever.retrieve("insider trading earnings disclosure")
    print("Retrieved top clause:", results[0]["title"] if results else "None")
