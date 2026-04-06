import os
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv
from google.genai.errors import ClientError
load_dotenv() 

# local embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts: list[str]) -> list[list[float]]:
    return embedding_model.encode(texts, normalize_embeddings=True).tolist()

def embed_query(text: str) -> list[float]:
    return embedding_model.encode([text], normalize_embeddings=True)[0].tolist()
