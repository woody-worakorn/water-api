# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class MachineBase(BaseModel):
    location: str
    status: str

class MachineCreate(MachineBase):
    pass

class Machine(MachineBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SlotBase(BaseModel):
    row: int
    column: int
    product_name: str
    price: float
    is_available: bool = True

class SlotCreate(SlotBase):
    machine_id: UUID

class Slot(SlotBase):
    id: UUID
    machine_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TransactionBase(BaseModel):
    slot_id: UUID
    user_id: Optional[UUID] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: UUID
    qr_code: str
    payment_status: str
    paid_at: Optional[datetime] = None
    webhook_received: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
