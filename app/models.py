from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Enum, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
# Change this line to use relative import
from .database import Base

class VendingMachine(Base):
    __tablename__ = "vending_machines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    slots = relationship("Slot", back_populates="machine")

class Slot(Base):
    __tablename__ = "slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("vending_machines.id"))
    row = Column(Integer)
    column = Column(Integer)
    product_name = Column(String)
    price = Column(Float)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    machine = relationship("VendingMachine", back_populates="slots")
    transactions = relationship("Transaction", back_populates="slot")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("slots.id"))
    charge_id = Column(String)  # Changed from payment_id to charge_id
    qr_code = Column(String)
    payment_status = Column(String)
    amount = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    slot = relationship("Slot", back_populates="transactions")
    api_events = relationship("APIEvent", back_populates="transaction")

class APIEvent(Base):
    __tablename__ = "api_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    event_type = Column(String)
    payload = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    transaction = relationship("Transaction", back_populates="api_events")
