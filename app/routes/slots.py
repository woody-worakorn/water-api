# app/routes/slots.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Slot
from typing import Optional
import uuid

router = APIRouter()

@router.get("/slots/{slot_id}")
def get_slot(slot_id: str, db: Session = Depends(get_db)):
    try:
        # Convert string to UUID
        slot_uuid = uuid.UUID(slot_id)

        # Query the slot
        slot = db.query(Slot).filter(Slot.id == slot_uuid).first()

        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")

        return {
            "id": str(slot.id),
            "machine_id": str(slot.machine_id),
            "row": slot.row,
            "column": slot.column,
            "product_name": slot.product_name,
            "price": slot.price,
            "is_available": slot.is_available,
            "created_at": slot.created_at,
            "updated_at": slot.updated_at
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
