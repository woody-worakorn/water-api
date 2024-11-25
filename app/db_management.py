# db_management.py
from database import engine, Base
import models

def reset_database():
    """Drop all tables and recreate them"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset completed")

if __name__ == "__main__":
    response = input("Are you sure you want to reset the database? This will delete all data! (y/N): ")
    if response.lower() == 'y':
        reset_database()
    else:
        print("Database reset cancelled")
