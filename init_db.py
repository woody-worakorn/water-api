# init_db.py
import os
import sys
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from app.database import SQLALCHEMY_DATABASE_URL, Base, engine
from app.models import *  # Import all models

def init_db():
    try:
        # Create database if it doesn't exist
        if not database_exists(SQLALCHEMY_DATABASE_URL):
            create_database(SQLALCHEMY_DATABASE_URL)
            print(f"Created database")

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print(f"Created all tables successfully")

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization completed")
