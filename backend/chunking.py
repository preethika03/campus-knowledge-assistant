from sqlalchemy.orm import Session

from models import Document, DocumentChunk


def split_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    """
    Split text into overlapping chunks.

    Example:
    chunk 1 → characters 0-500
    chunk 2 → characters 400-900
    chunk 3 → characters 800-1300
    """

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def create_document_chunks(
    db: Session,
    document_id: int,
    text: str
):
    """
    Split document text into chunks
    and save them into the database.
    """

    # Find the document
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise ValueError("Document not found")

    # Remove old chunks if they already exist
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()

    # Split text
    chunks = split_text(
        text=text,
        chunk_size=500,
        overlap=100
    )

    # Save each chunk
    for index, content in enumerate(chunks):

        chunk = DocumentChunk(
            document_id=document_id,
            chunk_index=index,
            content=content,
            character_count=len(content)
        )

        db.add(chunk)

    db.commit()

    return {
        "document_id": document_id,
        "chunks_created": len(chunks)
    }