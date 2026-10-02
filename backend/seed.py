from database import SessionLocal
from models import Role


def seed_roles():
    db = SessionLocal()

    roles = ["Student", "Faculty", "HOD", "Admin"]

    try:
        for role_name in roles:

            existing_role = (
                db.query(Role)
                .filter(Role.name == role_name)
                .first()
            )

            if not existing_role:
                db.add(Role(name=role_name))

        db.commit()

        print("Roles inserted successfully!")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_roles()