from sentence_transformers import CrossEncoder


# =========================================================
# RERANKING MODEL
# =========================================================

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker_model = CrossEncoder(MODEL_NAME)


# =========================================================
# RERANK RESULTS
# =========================================================

def rerank_results(
    query: str,
    results: list[dict],
    top_k: int = 3
) -> list[dict]:
    """
    Rerank retrieved document chunks using a CrossEncoder.

    Args:
        query: User's question.
        results: Results returned by semantic search.
        top_k: Number of results to return after reranking.

    Returns:
        Reranked results.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not results:
        return []

    # -----------------------------------------------------
    # Create query-document pairs
    # -----------------------------------------------------

    pairs = []

    for result in results:

        pairs.append(
            (
                query,
                result["content"]
            )
        )

    # -----------------------------------------------------
    # Generate reranking scores
    # -----------------------------------------------------

    scores = reranker_model.predict(pairs)

    # -----------------------------------------------------
    # Add score to every result
    # -----------------------------------------------------

    reranked_results = []

    for result, score in zip(results, scores):

        updated_result = result.copy()

        updated_result["rerank_score"] = float(score)

        reranked_results.append(updated_result)

    # -----------------------------------------------------
    # Sort by reranking score
    # Higher score = more relevant
    # -----------------------------------------------------

    reranked_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True
    )

    # -----------------------------------------------------
    # Return top results
    # -----------------------------------------------------

    return reranked_results[:top_k]


# =========================================================
# SIMPLE TEST
# =========================================================

if __name__ == "__main__":

    from secure_search import secure_semantic_search

    print("=" * 70)
    print("RERANKING TEST")
    print("=" * 70)

    user_id = 1

    query = "What are the attendance requirements?"

    print(f"\nUser ID: {user_id}")
    print(f"Question: {query}")

    # -----------------------------------------------------
    # First retrieve chunks using pgvector
    # -----------------------------------------------------

    results = secure_semantic_search(
        user_id=user_id,
        query=query,
        limit=5
    )

    print("\nInitial semantic search results:")
    print(f"Retrieved: {len(results)} chunks")

    # -----------------------------------------------------
    # Rerank the retrieved chunks
    # -----------------------------------------------------

    reranked = rerank_results(
        query=query,
        results=results,
        top_k=3
    )

    # -----------------------------------------------------
    # Display reranked results
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("RERANKED RESULTS")
    print("=" * 70)

    if not reranked:

        print("\nNo results found.")

    else:

        for index, result in enumerate(
            reranked,
            start=1
        ):

            print("\n" + "-" * 70)

            print(f"Result {index}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Document ID: {result['document_id']}")
            print(f"Chunk Index: {result['chunk_index']}")
            print(f"Semantic Similarity: {result['similarity']:.4f}")
            print(f"Rerank Score: {result['rerank_score']:.4f}")

            print("\nContent:")
            print(result["content"])

    print("\n" + "=" * 70)
    print("RERANKING TEST COMPLETED")
    print("=" * 70)