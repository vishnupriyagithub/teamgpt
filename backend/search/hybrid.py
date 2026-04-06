from rank_bm25 import BM25Okapi
import re

def tokenize(text: str):
    return re.findall(r"\w+", text.lower())


def keyword_search(query: str, documents: list[str], top_k=3):
    tokenized_docs = [tokenize(doc) for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    tokenized_query = tokenize(query)

    scores = bm25.get_scores(tokenized_query)
    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True
    )
    return [doc for doc, score in ranked[:top_k]]
