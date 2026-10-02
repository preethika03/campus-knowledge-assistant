from sqlalchemy import select

from database import SessionLocal
from models import DocumentChunk
from embeddings import generate_embedding


# =========================================================
# SEMANTIC SEARCH
# =========================================================

def semantic_search(
    query: str,
    limit: int = 5
):
    """
    Search document chunks using cosine similarity.

    Args:
        query: User's question.
        limit: Maximum number of chunks to return.

    Returns:
        List of matching chunks with similarity information.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    # -----------------------------------------------------
    # Convert the user's question into an embedding
    # -----------------------------------------------------

    query_embedding = generate_embedding(query)

    # -----------------------------------------------------
    # Open database session
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # Search using cosine distance
        # Smaller distance = more similar
        # -------------------------------------------------

        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        ).label("distance")

        statement = (
            select(
                DocumentChunk.id,
                DocumentChunk.document_id,
                DocumentChunk.chunk_index,
                DocumentChunk.content,
                distance
            )
            .where(
                DocumentChunk.embedding.is_not(None)
            )
            .order_by(distance)
            .limit(limit)
        )

        results = db.execute(statement).all()

        # -------------------------------------------------
        # Convert results into dictionaries
        # -------------------------------------------------

        formatted_results = []

        for row in results:

            # Convert cosine distance into similarity.
            # Distance normally ranges from 0 (very similar)
            # upward for normalized embeddings.
            similarity = 1 - float(row.distance)

            formatted_results.append({
                "chunk_id": row.id,
                "document_id": row.document_id,
                "chunk_index": row.chunk_index,
                "content": row.content,
                "distance": float(row.distance),
                "similarity": similarity
            })

        return formatted_results

    finally:
        db.close()


# =========================================================
# TEST SEARCH
# =========================================================

if __name__ == "__main__":

    test_query = "What are the attendance requirements?"

    print("=" * 70)
    print("SEMANTIC SEARCH TEST")
    print("=" * 70)

    print(f"\nQuery: {test_query}\n")

    results = semantic_search(
        test_query,
        limit=5
    )

    if not results:

        print("No matching chunks found.")

    else:

        for index, result in enumerate(results, start=1):

            print("-" * 70)
            print(f"Result {index}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Document ID: {result['document_id']}")
            print(f"Chunk Index: {result['chunk_index']}")
            print(f"Similarity: {result['similarity']:.4f}")
            print("\nContent:")
            print(result["content"])

    print("\n" + "=" * 70)
    print("SEARCH TEST COMPLETED")
    print("=" * 70)