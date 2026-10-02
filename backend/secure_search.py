from sqlalchemy import select

from database import SessionLocal
from models import (
    User,
    Document,
    DocumentChunk,
    DocumentPermission
)
from embeddings import generate_embedding


# =========================================================
# PERMISSION-AWARE SEMANTIC SEARCH
# =========================================================

def secure_semantic_search(
    user_id: int,
    query: str,
    limit: int = 5
):
    """
    Perform semantic search while respecting document permissions.

    Admin users can search all active documents.

    Other users can search only documents where they have
    an active DocumentPermission with can_view=True.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # Find the current user
        # -------------------------------------------------

        user = db.scalar(
            select(User).where(User.id == user_id)
        )

        if user is None:
            raise ValueError(
                f"User with ID {user_id} does not exist."
            )

        # -------------------------------------------------
        # Generate embedding for the question
        # -------------------------------------------------

        query_embedding = generate_embedding(query)

        # -------------------------------------------------
        # Calculate cosine distance
        # -------------------------------------------------

        distance = DocumentChunk.embedding.cosine_distance(
            query_embedding
        ).label("distance")

        # -------------------------------------------------
        # Base search query
        # -------------------------------------------------

        statement = (
            select(
                DocumentChunk.id,
                DocumentChunk.document_id,
                DocumentChunk.chunk_index,
                Document.title,
                Document.filename,
                DocumentChunk.content,
                distance
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id
            )
            .where(
                Document.is_active.is_(True),
                DocumentChunk.embedding.is_not(None)
            )
        )

        # -------------------------------------------------
        # ADMIN ACCESS
        # -------------------------------------------------

        if user.role.name == "Admin":

            print(f"User: {user.name}")
            print("Role: Admin")
            print("Access: All active documents")

        # -------------------------------------------------
        # NORMAL USER ACCESS
        # -------------------------------------------------

        else:

            allowed_documents = (
                select(DocumentPermission.document_id)
                .where(
                    DocumentPermission.user_id == user_id,
                    DocumentPermission.can_view.is_(True)
                )
            )

            statement = statement.where(
                DocumentChunk.document_id.in_(
                    allowed_documents
                )
            )

            print(f"User: {user.name}")
            print(f"Role: {user.role.name}")
            print("Access: Permission-based documents")

        # -------------------------------------------------
        # Sort by semantic similarity
        # -------------------------------------------------

        statement = (
            statement
            .order_by(distance)
            .limit(limit)
        )

        results = db.execute(statement).all()

        # -------------------------------------------------
        # Format results
        # -------------------------------------------------

        formatted_results = []

        for row in results:

            similarity = 1 - float(row.distance)

            formatted_results.append({
                "chunk_id": row.id,
                "document_id": row.document_id,
                "chunk_index": row.chunk_index,
                "title": row.title,
                "filename": row.filename,
                "content": row.content,
                "distance": float(row.distance),
                "similarity": similarity
            })

        return formatted_results

    finally:
        db.close()


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("PERMISSION-AWARE SEMANTIC SEARCH")
    print("=" * 70)

    try:

        # -------------------------------------------------
        # Ask for user ID
        # -------------------------------------------------

        user_id = int(
            input("\nEnter user ID: ").strip()
        )

        # -------------------------------------------------
        # Ask for question
        # -------------------------------------------------

        query = input(
            "Enter your question: "
        ).strip()

        # -------------------------------------------------
        # Perform search
        # -------------------------------------------------

        results = secure_semantic_search(
            user_id=user_id,
            query=query,
            limit=5
        )

        # -------------------------------------------------
        # Display results
        # -------------------------------------------------

        print("\n" + "=" * 70)
        print("SEARCH RESULTS")
        print("=" * 70)

        if not results:

            print("\nNo documents available for this user.")

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
                    f"Similarity: "
                    f"{result['similarity']:.4f}"
                )

                print("\nContent:")
                print(result["content"])

        print("\n" + "=" * 70)
        print("SEARCH COMPLETED")
        print("=" * 70)

    except ValueError as error:

        print(f"\nError: {error}")

    except Exception as error:

        print(
            f"\nUnexpected error: {error}"
        )