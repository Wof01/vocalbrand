"""Utility script to initialize VocalBrand SQLite DB."""
from auth import init_db, ensure_demo_user

if __name__ == "__main__":
    init_db()
    ensure_demo_user()
    print("Database initialized with demo user (demo@vocalbrand.local / demo123)")
