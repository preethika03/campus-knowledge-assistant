from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from sqlalchemy.orm import Session

from database import SessionLocal

from models import (
    Document,
    DocumentPermission,
    DocumentChunk,
    User
)

from permissions import require_admin

from auth import decode_access_token

from chunking import create_document_chunks

from embeddings import generate_embedding

import fitz
import os


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# =========================================================
# SECURITY
# =========================================================

security = HTTPBearer()


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# AUTHENTICATED USER
# =========================================================

def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(
            User.id == int(user_id)
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not user.is_active:

        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )

    return user


# =========================================================
# CREATE DOCUMENT
# =========================================================

@router.post("/")
def create_document(
    title: str,
    description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    document = Document(
        title=title,
        filename=None,
        description=description,
        uploaded_by=current_user.id,
        is_active=True
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    return {
        "success": True,
        "message": "Document created successfully",
        "document": {
            "id": document.id,
            "title": document.title,
            "filename": document.filename,
            "description": document.description,
            "uploaded_by": document.uploaded_by,
            "is_active": document.is_active
        }
    }


# =========================================================
# GET DOCUMENTS
# =========================================================

@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):

    role_name = ""

    if current_user.role:

        role_name = (
            current_user.role.name
            .strip()
            .lower()
        )

    # -----------------------------------------------------
    # ADMIN
    # -----------------------------------------------------

    if role_name == "admin":

        documents = (
            db.query(Document)
            .order_by(
                Document.created_at.desc()
            )
            .all()
        )

    # -----------------------------------------------------
    # OTHER USERS
    # -----------------------------------------------------

    else:

        documents = (
            db.query(Document)
            .join(
                DocumentPermission,
                Document.id ==
                DocumentPermission.document_id
            )
            .filter(
                DocumentPermission.user_id ==
                current_user.id,

                DocumentPermission.can_view ==
                True,

                Document.is_active ==
                True
            )
            .order_by(
                Document.created_at.desc()
            )
            .all()
        )

    return {
        "success": True,
        "count": len(documents),
        "documents": [
            {
                "id": document.id,
                "title": document.title,
                "filename": document.filename,
                "description": document.description,
                "uploaded_by": document.uploaded_by,
                "is_active": document.is_active
            }
            for document in documents
        ]
    }


# =========================================================
# UPDATE DOCUMENT STATUS
# =========================================================

@router.patch("/{document_id}/status")
def update_document_status(
    document_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document.is_active = is_active

    db.commit()

    db.refresh(document)

    return {
        "success": True,
        "message": (
            "Document activated successfully"
            if is_active
            else
            "Document deactivated successfully"
        ),
        "document_id": document.id,
        "is_active": document.is_active
    }


# =========================================================
# GRANT DOCUMENT PERMISSION
# =========================================================

@router.post("/{document_id}/permissions")
def grant_document_permission(
    document_id: int,
    user_id: int,
    can_read: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    user = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    existing_permission = (
        db.query(DocumentPermission)
        .filter(
            DocumentPermission.document_id ==
            document_id,

            DocumentPermission.user_id ==
            user_id
        )
        .first()
    )

    if existing_permission:

        existing_permission.can_view = can_read

        db.commit()

        return {
            "success": True,
            "message":
                "Document permission updated successfully",
            "document_id": document_id,
            "user_id": user_id,
            "can_read": can_read
        }

    permission = DocumentPermission(
        document_id=document_id,
        user_id=user_id,
        can_view=can_read
    )

    db.add(permission)

    db.commit()

    return {
        "success": True,
        "message":
            "Document permission granted successfully",
        "document_id": document_id,
        "user_id": user_id,
        "can_read": can_read
    }


# =========================================================
# UPLOAD PDF
# =========================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing"
        )

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_bytes = await file.read()

    try:

        pdf = fitz.open(
            stream=file_bytes,
            filetype="pdf"
        )

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    extracted_text = ""

    for page in pdf:

        extracted_text += page.get_text()
        extracted_text += "\n"

    pdf.close()

    if not extracted_text.strip():

        raise HTTPException(
            status_code=400,
            detail="No readable text found in PDF"
        )

    document = Document(
        title=os.path.splitext(
            file.filename
        )[0],

        filename=file.filename,

        description="Uploaded PDF document",

        uploaded_by=current_user.id,

        is_active=True
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    chunk_result = create_document_chunks(
        db=db,
        document_id=document.id,
        text=extracted_text
    )

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id ==
            document.id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .all()
    )

    embeddings_created = 0

    try:

        for chunk in chunks:

            embedding = generate_embedding(
                chunk.content
            )

            chunk.embedding = embedding

            embeddings_created += 1

        db.commit()

    except Exception as error:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document was uploaded and chunked, "
                "but embedding generation failed: "
                f"{str(error)}"
            )
        )

    return {
        "success": True,

        "message": (
            "PDF uploaded, text extracted, "
            "chunked and embedded successfully"
        ),

        "document_id": document.id,

        "filename": file.filename,

        "text_length": len(extracted_text),

        "chunks_created":
            chunk_result["chunks_created"],

        "embeddings_created":
            embeddings_created,

        "is_active":
            document.is_active,

        "text_preview":
            extracted_text[:2000]
    }