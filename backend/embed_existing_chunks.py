import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import DocumentChunk
from embeddings import generate_embedding


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL was not found in the .env file."
    )


# =========================================================
# DATABASE CONNECTION
# =========================================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# =========================================================
# EMBED EXISTING CHUNKS
# =========================================================

def embed_existing_chunks():
    print("=" * 60)
    print("Embedding existing document chunks")
    print("=" * 60)

    with Session(engine) as session:

        statement = (
            select(DocumentChunk)
            .where(DocumentChunk.embedding.is_(None))
            .order_by(DocumentChunk.id)
        )

        chunks = session.scalars(statement).all()

        print(f"Chunks found without embeddings: {len(chunks)}")

        if not chunks:
            print("All chunks already have embeddings.")
            return

        for chunk in chunks:

            print()
            print(f"Processing chunk ID: {chunk.id}")
            print(f"Document ID: {chunk.document_id}")
            print(f"Chunk index: {chunk.chunk_index}")

            embedding = generate_embedding(
                chunk.content
            )

            if len(embedding) != 384:
                raise ValueError(
                    f"Expected 384 dimensions, "
                    f"but received {len(embedding)}."
                )

            chunk.embedding = embedding

            print("Embedding generated successfully.")
            print(f"Vector dimensions: {len(embedding)}")

        session.commit()

        print()
        print("=" * 60)
        print("SUCCESS: All embeddings saved to PostgreSQL.")
        print("=" * 60)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    embed_existing_chunks()