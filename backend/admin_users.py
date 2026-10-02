from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from database import SessionLocal

from models import User, Role

from auth import hash_password

from permissions import require_admin


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


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
# GET USERS
# =========================================================

@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    users = (
        db.query(User)
        .order_by(
            User.id
        )
        .all()
    )

    return {
        "success": True,
        "count": len(users),

        "users": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role_id": user.role_id,
                "role": (
                    user.role.name
                    if user.role
                    else None
                ),
                "is_active": user.is_active
            }

            for user in users
        ]
    }


# =========================================================
# CREATE USER
# =========================================================

@router.post("/users")
def create_user(
    name: str,
    email: str,
    password: str,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    # -----------------------------------------------------
    # CHECK EMAIL
    # -----------------------------------------------------

    existing_user = (
        db.query(User)
        .filter(
            User.email == email
        )
        .first()
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # -----------------------------------------------------
    # FIND ROLE
    # -----------------------------------------------------

    role = (
        db.query(Role)
        .filter(
            Role.id == role_id
        )
        .first()
    )

    if not role:

        raise HTTPException(
            status_code=400,
            detail="Invalid role ID"
        )


    # -----------------------------------------------------
    # PREVENT ADMIN CREATION
    # -----------------------------------------------------

    role_name = (
        role.name
        .strip()
        .lower()
    )

    if role_name == "admin":

        raise HTTPException(
            status_code=403,
            detail="Admin accounts cannot be created through this endpoint"
        )


    # -----------------------------------------------------
    # VALIDATE ALLOWED ROLES
    # -----------------------------------------------------

    allowed_roles = [
        "student",
        "faculty",
        "hod"
    ]

    if role_name not in allowed_roles:

        raise HTTPException(
            status_code=400,
            detail=(
                "Allowed roles are Student, Faculty and HOD"
            )
        )


    # -----------------------------------------------------
    # BASIC PASSWORD CHECK
    # -----------------------------------------------------

    if len(password) < 6:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters"
        )


    # -----------------------------------------------------
    # HASH PASSWORD
    # -----------------------------------------------------

    hashed_password = hash_password(
        password
    )


    # -----------------------------------------------------
    # CREATE USER
    # -----------------------------------------------------

    new_user = User(

        name=name,

        email=email,

        password_hash=hashed_password,

        role_id=role.id,

        is_active=True
    )


    db.add(new_user)

    db.commit()

    db.refresh(new_user)


    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {
        "success": True,

        "message":
            "User created successfully",

        "user": {

            "id":
                new_user.id,

            "name":
                new_user.name,

            "email":
                new_user.email,

            "role_id":
                new_user.role_id,

            "role":
                role.name,

            "is_active":
                new_user.is_active
        }
    }


# =========================================================
# UPDATE USER STATUS
# =========================================================

@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):

    # -----------------------------------------------------
    # FIND USER
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # PREVENT SELF-DEACTIVATION
    # -----------------------------------------------------

    if (
        user.id == current_user.id
        and not is_active
    ):

        raise HTTPException(
            status_code=400,
            detail="You cannot deactivate your own account"
        )


    # -----------------------------------------------------
    # UPDATE STATUS
    # -----------------------------------------------------

    user.is_active = is_active

    db.commit()

    db.refresh(user)


    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "success": True,

        "message": (
            "User activated successfully"
            if is_active
            else "User deactivated successfully"
        ),

        "user_id":
            user.id,

        "is_active":
            user.is_active
    }