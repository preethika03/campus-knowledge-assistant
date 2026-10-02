from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from database import SessionLocal

from models import (
    User,
    ChatMessage
)

from auth import decode_access_token

from rag_answer import generate_rag_answer


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


# =========================================================
# SECURITY
# =========================================================

security = HTTPBearer()


# =========================================================
# REQUEST SCHEMA
# =========================================================

class ChatRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="Question asked by the user"
    )


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:

    # -----------------------------------------------------
    # Get token
    # -----------------------------------------------------

    token = credentials.credentials

    # -----------------------------------------------------
    # Decode token
    # -----------------------------------------------------

    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    # -----------------------------------------------------
    # Get user ID
    # -----------------------------------------------------

    user_id = payload.get("sub")

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    # -----------------------------------------------------
    # Database connection
    # -----------------------------------------------------

    db: Session = SessionLocal()

    try:

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

        # -------------------------------------------------
        # Check account status
        # -------------------------------------------------

        if not user.is_active:

            raise HTTPException(
                status_code=403,
                detail="User account is inactive"
            )

        return user

    finally:

        db.close()


# =========================================================
# CHAT
# =========================================================

@router.post("/")
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):

    try:

        # -------------------------------------------------
        # Generate RAG answer
        # -------------------------------------------------

        result = generate_rag_answer(
            user_id=current_user.id,
            question=request.question
        )

        # -------------------------------------------------
        # Extract answer and sources
        # -------------------------------------------------

        answer = result["answer"]

        sources = result.get(
            "sources",
            []
        )

        # -------------------------------------------------
        # Save conversation
        # -------------------------------------------------

        db: Session = SessionLocal()

        try:

            chat_message = ChatMessage(
                user_id=current_user.id,
                question=request.question,
                answer=answer,
                sources=sources
            )

            db.add(chat_message)

            db.commit()

            db.refresh(chat_message)

            chat_message_id = chat_message.id

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

        # -------------------------------------------------
        # Return response
        # -------------------------------------------------

        return {
            "success": True,
            "message_id": chat_message_id,
            "question": request.question,
            "answer": answer,
            "sources": sources
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Chat generation failed: {str(error)}"
        )


# =========================================================
# CHAT HISTORY
# =========================================================

@router.get("/history")
def get_chat_history(
    current_user: User = Depends(get_current_user)
):

    db: Session = SessionLocal()

    try:

        messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == current_user.id
            )
            .order_by(
                ChatMessage.created_at.desc()
            )
            .all()
        )

        history = []

        for message in messages:

            history.append({
                "id": message.id,
                "question": message.question,
                "answer": message.answer,
                "sources": message.sources or [],
                "created_at": message.created_at
            })

        return {
            "success": True,
            "count": len(history),
            "history": history
        }

    finally:

        db.close()