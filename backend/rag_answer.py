from retrieval import retrieve_relevant_chunks
from llm import generate_answer


# =========================================================
# BUILD CONTEXT
# =========================================================

def build_context(results: list[dict]) -> str:
    """
    Convert retrieved chunks into a structured context
    that can be given to the LLM.
    """

    context_parts = []

    for index, result in enumerate(results, start=1):

        source_text = (
            f"[Source {index}]\n"
            f"Document: {result['title']}\n"
            f"Filename: {result['filename']}\n"
            f"Chunk ID: {result['chunk_id']}\n"
            f"Content:\n{result['content']}\n"
        )

        context_parts.append(source_text)

    return "\n" + "\n".join(context_parts)


# =========================================================
# GENERATE RAG ANSWER
# =========================================================

def generate_rag_answer(
    user_id: int,
    question: str
) -> dict:
    """
    Complete RAG pipeline:

    1. Permission-aware retrieval
    2. Semantic search
    3. Reranking
    4. Context creation
    5. LLM answer generation
    """

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # -----------------------------------------------------
    # Retrieve relevant chunks
    # -----------------------------------------------------

    results = retrieve_relevant_chunks(
        user_id=user_id,
        query=question,
        candidate_limit=5,
        top_k=3
    )

    if not results:
        return {
            "answer": (
                "I could not find any documents that you "
                "are authorized to access for this question."
            ),
            "sources": []
        }

    # -----------------------------------------------------
    # Build context
    # -----------------------------------------------------

    context = build_context(results)

    # -----------------------------------------------------
    # Create LLM prompt
    # -----------------------------------------------------

    prompt = f"""
You are the Campus Knowledge Assistant.

Answer the user's question using ONLY the information
provided in the retrieved document context.

IMPORTANT RULES:

1. Do not use outside knowledge.
2. Do not invent information.
3. If the context does not contain the answer, say:
   "The available documents do not contain enough information
   to answer this question."
4. Keep the answer clear and concise.
5. Cite the source after factual statements using:
   [Source 1], [Source 2], etc.
6. Use only the source numbers that actually support the answer.

USER QUESTION:
{question}

RETRIEVED DOCUMENT CONTEXT:
{context}

Now answer the user's question.
"""

    # -----------------------------------------------------
    # Generate answer using Gemini
    # -----------------------------------------------------

    answer = generate_answer(prompt)

    # -----------------------------------------------------
    # Return answer + source information
    # -----------------------------------------------------

    sources = []

    for index, result in enumerate(results, start=1):

        sources.append({
            "source": f"Source {index}",
            "document_id": result["document_id"],
            "chunk_id": result["chunk_id"],
            "chunk_index": result["chunk_index"],
            "title": result["title"],
            "filename": result["filename"]
        })

    return {
        "answer": answer,
        "sources": sources
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("CAMPUS KNOWLEDGE ASSISTANT - RAG TEST")
    print("=" * 70)

    try:

        # -------------------------------------------------
        # User ID
        # -------------------------------------------------

        user_id = int(
            input("\nEnter user ID: ").strip()
        )

        # -------------------------------------------------
        # Question
        # -------------------------------------------------

        question = input(
            "Enter your question: "
        ).strip()

        # -------------------------------------------------
        # Generate answer
        # -------------------------------------------------

        result = generate_rag_answer(
            user_id=user_id,
            question=question
        )

        # -------------------------------------------------
        # Display answer
        # -------------------------------------------------

        print("\n" + "=" * 70)
        print("ANSWER")
        print("=" * 70)

        print("\n" + result["answer"])

        # -------------------------------------------------
        # Display sources
        # -------------------------------------------------

        print("\n" + "=" * 70)
        print("SOURCES")
        print("=" * 70)

        if not result["sources"]:

            print("\nNo sources available.")

        else:

            for source in result["sources"]:

                print(
                    f"\n{source['source']}"
                )

                print(
                    f"Document: "
                    f"{source['title']}"
                )

                print(
                    f"Filename: "
                    f"{source['filename']}"
                )

                print(
                    f"Chunk ID: "
                    f"{source['chunk_id']}"
                )

                print(
                    f"Chunk Index: "
                    f"{source['chunk_index']}"
                )

        print("\n" + "=" * 70)
        print("RAG TEST COMPLETED")
        print("=" * 70)

    except ValueError as error:

        print(f"\nError: {error}")

    except Exception as error:

        print(
            f"\nUnexpected error: {error}"
        )