# seed_db.py
import uuid
from backend.app.database import SessionLocal
import backend.app.models as models

def seed_database():
    db = SessionLocal()
    try:
        # Create a vending machine
        machine = models.VendingMachine(
            id=uuid.uuid4(),
            location="Main Building",
            status="active"
        )
        db.add(machine)
        db.commit()
        db.refresh(machine)

        # Create 30 slots (5x6 grid)
        slots = []
        for row in range(1, 6):
            for col in range(1, 7):
                slot = models.Slot(
                    id=uuid.uuid4(),
                    machine_id=machine.id,
                    row=row,
                    column=col,
                    product_name="Water Bottle",
                    price=20.0,
                    is_available=True
                )
                slots.append(slot)

        db.add_all(slots)
        db.commit()

        print(f"Created machine with ID: {machine.id}")
        print(f"Created {len(slots)} slots")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding database...")
    seed_database()
    print("Database seeding completed")
