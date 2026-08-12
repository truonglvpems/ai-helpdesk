import uuid

from app.core.database import SessionLocal
from app.models import Organization, User, TicketCategory


def seed():
    db = SessionLocal()

    try:
        # =========================================================
        # 1. Organization
        # =========================================================

        organization = (
            db.query(Organization)
            .filter(Organization.slug == "acme")
            .first()
        )

        if organization is None:
            organization = Organization(
                name="Acme Corporation",
                slug="acme",
                status="active",
            )

            db.add(organization)
            db.flush()

            print(f"[CREATE] Organization: {organization.name}")
            print(f"         ID: {organization.id}")

        else:
            print(f"[EXISTS] Organization: {organization.name}")
            print(f"         ID: {organization.id}")

        # =========================================================
        # 2. Users
        # =========================================================

        users_data = [
            {
                "email": "admin@acme.local",
                "full_name": "System Administrator",
                "role": "ADMIN",
            },
            {
                "email": "employee@acme.local",
                "full_name": "John Employee",
                "role": "EMPLOYEE",
            },
            {
                "email": "technician@acme.local",
                "full_name": "IT Technician",
                "role": "TECHNICIAN",
            },
        ]

        users = {}

        for data in users_data:

            user = (
                db.query(User)
                .filter(User.email == data["email"])
                .first()
            )

            if user is None:
                user = User(
                    organization_id=organization.id,
                    auth_user_id=uuid.uuid4(),
                    email=data["email"],
                    full_name=data["full_name"],
                    role=data["role"],
                    status="active",
                )

                db.add(user)
                db.flush()

                print(
                    f"[CREATE] User: {user.email} "
                    f"({user.role})"
                )

            else:
                print(
                    f"[EXISTS] User: {user.email} "
                    f"({user.role})"
                )

            users[data["email"]] = user

        # =========================================================
        # 3. Ticket Categories
        # =========================================================

        categories = [
            "Hardware",
            "Software",
            "Network",
            "Account & Access",
        ]

        for category_name in categories:

            category = (
                db.query(TicketCategory)
                .filter(
                    TicketCategory.organization_id == organization.id,
                    TicketCategory.name == category_name,
                )
                .first()
            )

            if category is None:
                category = TicketCategory(
                    organization_id=organization.id,
                    name=category_name,
                    is_active=True,
                )

                db.add(category)
                db.flush()

                print(
                    f"[CREATE] Category: {category.name}"
                )

            else:
                print(
                    f"[EXISTS] Category: {category.name}"
                )

        # =========================================================
        # 4. Commit
        # =========================================================

        db.commit()

        print()
        print("=" * 60)
        print("Development seed completed successfully.")
        print("=" * 60)

        print()
        print("Organization:")
        print(f"  ID   : {organization.id}")
        print(f"  Name : {organization.name}")
        print(f"  Slug : {organization.slug}")

        print()
        print("Users:")

        for email, user in users.items():
            print(
                f"  {user.email:<30} "
                f"{user.role:<12} "
                f"{user.id}"
            )

        print()
        print("Categories:")

        for category_name in categories:
            print(f"  - {category_name}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()