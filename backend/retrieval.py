from secure_search import secure_semantic_search
from reranker import rerank_results


# =========================================================
# COMPLETE RETRIEVAL PIPELINE
# =========================================================

def retrieve_relevant_chunks(
    user_id: int,
    query: str,
    candidate_limit: int = 5,
    top_k: int = 3
) -> list[dict]:
    """
    Complete RAG retrieval pipeline.

    Step 1:
        Permission-aware semantic search using pgvector.

    Step 2:
        Rerank the retrieved chunks using CrossEncoder.

    Args:
        user_id: ID of the logged-in user.
        query: User's question.
        candidate_limit: Number of chunks retrieved from pgvector.
        top_k: Number of chunks returned after reranking.

    Returns:
        Top relevant, permission-filtered chunks.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    # -----------------------------------------------------
    # STEP 1: Permission-aware semantic search
    # -----------------------------------------------------

    candidates = secure_semantic_search(
        user_id=user_id,
        query=query,
        limit=candidate_limit
    )

    if not candidates:
        return []

    # -----------------------------------------------------
    # STEP 2: Rerank the candidates
    # -----------------------------------------------------

    final_results = rerank_results(
        query=query,
        results=candidates,
        top_k=top_k
    )

    return final_results


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("COMPLETE RETRIEVAL PIPELINE TEST")
    print("=" * 70)

    user_id = 1

    query = "What are the attendance requirements?"

    print(f"\nUser ID: {user_id}")
    print(f"Question: {query}")

    results = retrieve_relevant_chunks(
        user_id=user_id,
        query=query,
        candidate_limit=5,
        top_k=3
    )

    print("\n" + "=" * 70)
    print("FINAL RETRIEVED CONTEXT")
    print("=" * 70)

    if not results:

        print("\nNo relevant documents found.")

    else:

        for index, result in enumerate(
            results,
            start=1
        ):

            print("\n" + "-" * 70)

            print(f"Result {index}")
            print(f"Document ID: {result['document_id']}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Chunk Index: {result['chunk_index']}")
            print(f"Title: {result['title']}")
            print(f"Filename: {result['filename']}")
            print(
                f"Semantic Similarity: "
                f"{result['similarity']:.4f}"
            )
            print(
                f"Rerank Score: "
                f"{result['rerank_score']:.4f}"
            )

            print("\nContent:")
            print(result["content"])

    print("\n" + "=" * 70)
    print("RETRIEVAL PIPELINE TEST COMPLETED")
    print("=" * 70)