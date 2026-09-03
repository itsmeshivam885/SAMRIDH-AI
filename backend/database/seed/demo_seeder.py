#!/usr/bin/env python3
"""
SAMRIDH Demo Seeder — Team TwinBit
===================================
Clears existing user tables, creates database schema, and seeds the 6 exact default accounts.
"""

import sys
import os
from pathlib import Path

# Force UTF-8 output if supported
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.core.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.officer import Officer
from app.core.security import get_password_hash

DEFAULT_USERS = [
    {
        "full_name": "ARYAN SINGH",
        "registration_no": "25BCE10798",
        "username": "aryan.25bce10798",
        "raw_password": "Aryan#25BCE10798!Sec2026",
        "role": UserRole.FARMER,
    },
    {
        "full_name": "SHIVAM SINGH",
        "registration_no": "25BCE10736",
        "username": "shivam.25bce10736",
        "raw_password": "Shivam#25BCE10736!Sec2026",
        "role": UserRole.FARMER,
    },
    {
        "full_name": "ATHARV BISHT",
        "registration_no": "25BCE10596",
        "username": "atharv.25bce10596",
        "raw_password": "Atharv#25BCE10596!Sec2026",
        "role": UserRole.FARMER,
    },
    {
        "full_name": "KRISHNA AGRAWAL",
        "registration_no": "25BCE10117",
        "username": "krishna.25bce10117",
        "raw_password": "Krishna#25BCE10117!Sec2026",
        "role": UserRole.FIELD_OFFICER,
    },
    {
        "full_name": "RESHMA RANI AGASTI",
        "registration_no": "25BCE10240",
        "username": "reshma.25bce10240",
        "raw_password": "Reshma#25BCE10240!Sec2026",
        "role": UserRole.INSURER,
    },
    {
        "full_name": "RAKHI TYAGI",
        "registration_no": "25BCE10780",
        "username": "rakhi.25bce10780",
        "raw_password": "Rakhi#25BCE10780!Sec2026",
        "role": UserRole.SUPER_ADMIN,
    },
]


def seed_database():
    print("=" * 65)
    print("SAMRIDH - Seeding Authentication & RBAC User Data")
    print("=" * 65)

    print("[1/3] Resetting database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("      Tables recreated successfully.")

    db: Session = SessionLocal()
    try:
        print("[2/3] Seeding 6 default accounts...")
        for udata in DEFAULT_USERS:
            hashed_pwd = get_password_hash(udata["raw_password"])
            user = User(
                username=udata["username"],
                registration_no=udata["registration_no"],
                full_name=udata["full_name"],
                hashed_password=hashed_pwd,
                role=udata["role"],
                is_active=True,
            )
            db.add(user)
            db.flush()

            if udata["role"] == UserRole.FARMER:
                farmer = Farmer(
                    user_id=user.id,
                    farmer_id_code=f"FARMER-{udata['registration_no']}",
                    state="Madhya Pradesh",
                    district="Sehore",
                    village="Ashta",
                )
                db.add(farmer)
            elif udata["role"] == UserRole.FIELD_OFFICER:
                officer = Officer(
                    user_id=user.id,
                    officer_badge_number=f"BADGE-{udata['registration_no']}",
                    designation="District Agricultural Loss Assessor",
                    assigned_state="Madhya Pradesh",
                    assigned_district="Sehore",
                )
                db.add(officer)

            print(f"      + Created User: {user.full_name:<20} | Username: {user.username:<18} | Role: {user.role.value}")

        db.commit()
        print("[3/3] Database commit complete!")
        print("=" * 65)
        print("SUCCESS: Authentication database initialized & seeded.")
        print("=" * 65)

    except Exception as e:
        db.rollback()
        print(f"ERROR during database seeding: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
