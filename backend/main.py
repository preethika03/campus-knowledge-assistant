import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://127.0.0.1:5173"
)

from sqlalchemy import (
    text,
    func
)

from sqlalchemy.orm import Session

from database import (
    engine,
    Base,
    SessionLocal
)

from models import User, Role

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

from schemas import (
    UserCreate,
    UserLogin
)

from permissions import (
    require_student,
    require_faculty,
    require_hod,
    require_admin
)

from documents import router as documents_router

from chat import router as chat_router

from admin_users import router as admin_users_router


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Campus Knowledge Assistant",
    description="AI-powered university knowledge assistant",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
    FRONTEND_URL
],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# =========================================================
# AUTHENTICATION
# =========================================================

security = HTTPBearer()


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

Base.metadata.create_all(
    bind=engine
)


# =========================================================
# ROUTERS
# =========================================================

app.include_router(
    documents_router
)

app.include_router(
    chat_router
)

app.include_router(
    admin_users_router
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message":
            "Campus Knowledge Assistant API is running 🚀"
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health_check():

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:

        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


# =========================================================
# REGISTER USER
# =========================================================

@app.post("/register")
def register_user(
    user_data: UserCreate
):

    db: Session = SessionLocal()

    try:

        # -------------------------------------------------
        # CHECK WHETHER EMAIL ALREADY EXISTS
        # -------------------------------------------------

        existing_user = (
            db.query(User)
            .filter(
                User.email ==
                user_data.email
            )
            .first()
        )

        if existing_user:

            return {
                "success": False,
                "message":
                    "Email already registered"
            }


        # -------------------------------------------------
        # ALWAYS USE THE STUDENT ROLE
        # -------------------------------------------------
        #
        # We intentionally DO NOT trust
        # user_data.role_id.
        #
        # Public registration creates
        # Student accounts only.
        #

        student_role = (
            db.query(Role)
            .filter(
                func.lower(Role.name) ==
                "student"
            )
            .first()
        )

        if not student_role:

            return {
                "success": False,
                "message":
                    "Student role not found in database"
            }


        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------

        hashed_password = hash_password(
            user_data.password
        )


        # -------------------------------------------------
        # CREATE STUDENT USER
        # -------------------------------------------------

        new_user = User(
            name=user_data.name,

            email=user_data.email,

            password_hash=hashed_password,

            role_id=student_role.id,

            is_active=True
        )

        db.add(new_user)

        db.commit()

        db.refresh(new_user)


        # -------------------------------------------------
        # RETURN RESPONSE
        # -------------------------------------------------

        return {
            "success": True,

            "message":
                "Student account registered successfully",

            "user_id":
                new_user.id,

            "role":
                student_role.name
        }


    except Exception as e:

        db.rollback()

        return {
            "success": False,

            "message":
                "Registration failed",

            "error":
                str(e)
        }


    finally:

        db.close()


# =========================================================
# LOGIN
# =========================================================

@app.post("/login")
def login_user(
    user_data: UserLogin
):

    db: Session = SessionLocal()

    try:

        # -------------------------------------------------
        # FIND USER
        # -------------------------------------------------

        user = (
            db.query(User)
            .filter(
                User.email ==
                user_data.email
            )
            .first()
        )

        if not user:

            return {
                "success": False,
                "message":
                    "Invalid email or password"
            }


        # -------------------------------------------------
        # CHECK ACTIVE STATUS
        # -------------------------------------------------

        if not user.is_active:

            return {
                "success": False,
                "message":
                    "Account is inactive"
            }


        # -------------------------------------------------
        # VERIFY PASSWORD
        # -------------------------------------------------

        if not verify_password(
            user_data.password,
            user.password_hash
        ):

            return {
                "success": False,
                "message":
                    "Invalid email or password"
            }


        # -------------------------------------------------
        # CREATE JWT
        # -------------------------------------------------

        access_token = create_access_token(
            {
                "sub":
                    str(user.id),

                "email":
                    user.email,

                "role_id":
                    user.role_id
            }
        )


        # -------------------------------------------------
        # RETURN LOGIN RESPONSE
        # -------------------------------------------------

        return {
            "success": True,

            "message":
                "Login successful",

            "access_token":
                access_token,

            "token_type":
                "bearer",

            "user": {

                "id":
                    user.id,

                "name":
                    user.name,

                "email":
                    user.email,

                "role_id":
                    user.role_id
            }
        }


    except Exception as e:

        return {
            "success": False,

            "message":
                "Login failed",

            "error":
                str(e)
        }


    finally:

        db.close()


# =========================================================
# CURRENT USER
# =========================================================

@app.get("/users/me")
def get_current_user(
    credentials:
        HTTPAuthorizationCredentials =
        Depends(security)
):

    # -----------------------------------------------------
    # GET TOKEN
    # -----------------------------------------------------

    token = credentials.credentials


    # -----------------------------------------------------
    # DECODE TOKEN
    # -----------------------------------------------------

    payload = decode_access_token(
        token
    )

    if not payload:

        return {
            "success": False,

            "message":
                "Invalid or expired token"
        }


    # -----------------------------------------------------
    # GET USER ID
    # -----------------------------------------------------

    user_id = payload.get(
        "sub"
    )

    if not user_id:

        return {
            "success": False,

            "message":
                "Invalid token"
        }


    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    db: Session = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.id ==
                int(user_id)
            )
            .first()
        )

        if not user:

            return {
                "success": False,

                "message":
                    "User not found"
            }


        # -------------------------------------------------
        # RETURN CURRENT USER
        # -------------------------------------------------

        return {
            "success": True,

            "user": {

                "id":
                    user.id,

                "name":
                    user.name,

                "email":
                    user.email,

                "role_id":
                    user.role_id,

                "is_active":
                    user.is_active
            }
        }


    finally:

        db.close()


# =========================================================
# RBAC TEST - STUDENT
# =========================================================

@app.get("/rbac/student")
def student_area(
    current_user:
        User =
        Depends(require_student)
):

    return {
        "success": True,

        "message":
            "Welcome to the Student area",

        "user":
            current_user.name,

        "role":
            "Student"
    }


# =========================================================
# RBAC TEST - FACULTY
# =========================================================

@app.get("/rbac/faculty")
def faculty_area(
    current_user:
        User =
        Depends(require_faculty)
):

    return {
        "success": True,

        "message":
            "Welcome to the Faculty area",

        "user":
            current_user.name
    }


# =========================================================
# RBAC TEST - HOD
# =========================================================

@app.get("/rbac/hod")
def hod_area(
    current_user:
        User =
        Depends(require_hod)
):

    return {
        "success": True,

        "message":
            "Welcome to the HOD area",

        "user":
            current_user.name
    }


# =========================================================
# RBAC TEST - ADMIN
# =========================================================

@app.get("/rbac/admin")
def admin_area(
    current_user:
        User =
        Depends(require_admin)
):

    return {
        "success": True,

        "message":
            "Welcome to the Admin area",

        "user":
            current_user.name
    }