from sentence_transformers import SentenceTransformer


# =========================================================
# EMBEDDING MODEL
# =========================================================

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


# =========================================================
# GENERATE EMBEDDING
# =========================================================

def generate_embedding(text: str) -> list[float]:
    """
    Convert text into a 384-dimensional embedding vector.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()