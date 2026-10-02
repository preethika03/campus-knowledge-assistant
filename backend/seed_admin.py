from database import SessionLocal
from models import User, Role
from auth import hash_password


# ==========================================
# CREATE ADMIN TEST USER
# ==========================================

db = SessionLocal()

try:

    # Find Admin role
    admin_role = (
        db.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if not admin_role:
        print("❌ Admin role not found")
        print("Make sure the roles table contains the Admin role.")
        exit()

    # Check whether admin already exists
    existing_admin = (
        db.query(User)
        .filter(User.email == "admin@example.com")
        .first()
    )

    if existing_admin:

        print("⚠️ Admin user already exists")

    else:

        # Create Admin
        admin = User(
            name="Test Admin",
            email="admin@example.com",
            password_hash=hash_password("AdminPassword123"),
            role_id=admin_role.id,
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("✅ Admin user created successfully")
        print()
        print("Email: admin@example.com")
        print("Password: AdminPassword123")
        print("Role: Admin")
        print("User ID:", admin.id)

finally:

    db.close()