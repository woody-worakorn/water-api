# app/routes/payment.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict
from ..database import get_db
from ..models import Slot, Transaction
from ..config import settings
import requests
from datetime import datetime

router = APIRouter()

OPNPAYMENTS_API = "https://api.omise.co"

@router.post("/payment/create")
async def create_payment(data: Dict, db: Session = Depends(get_db)):
    try:
        # Verify slot exists and is available
        slot = db.query(Slot).filter(Slot.id == data["slot_id"]).first()
        if not slot or not slot.is_available:
            raise HTTPException(status_code=400, detail="Slot not available")

        amount = int(data["amount"])

        # Create source
        source_response = requests.post(
            f"{OPNPAYMENTS_API}/sources",
            auth=(settings.OPN_SECRET_KEY, ""),
            json={
                "type": "promptpay",
                "amount": amount,
                "currency": "THB"
            }
        )

        if not source_response.ok:
            print("Source creation failed:", source_response.text)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create source: {source_response.json()}"
            )

        source = source_response.json()

        # Create charge
        charge_response = requests.post(
            f"{OPNPAYMENTS_API}/charges",
            auth=(settings.OPN_SECRET_KEY, ""),
            json={
                "amount": amount,
                "currency": "THB",
                "source": source["id"]
            }
        )

        if not charge_response.ok:
            print("Charge creation failed:", charge_response.text)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to create charge: {charge_response.json()}"
            )

        charge = charge_response.json()

        # Get QR code URL
        qr_code_url = charge["source"]["scannable_code"]["image"]["download_uri"]

        # Create transaction record using the correct field names
        transaction = Transaction(
            slot_id=slot.id,
            charge_id=charge["id"],  # Using charge_id instead of payment_id
            qr_code=qr_code_url,
            payment_status="pending",
            amount=amount / 100,  # Convert to baht
        )

        # Lock the slot
        slot.is_available = False

        # Save to database
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return {
            "success": True,
            "qrCode": qr_code_url,
            "chargeId": charge["id"],
            "amount": amount / 100
        }

    except Exception as e:
        print("Error in create_payment:", str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment/status/{charge_id}")
async def check_payment_status(charge_id: str, db: Session = Depends(get_db)):
    try:
        # Retrieve charge from Opn Payments
        response = requests.get(
            f"{OPNPAYMENTS_API}/charges/{charge_id}",
            auth=(settings.OPN_SECRET_KEY, "")
        )

        if not response.ok:
            print("Status check failed:", response.text)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to retrieve charge: {response.json()}"
            )

        charge = response.json()

        # Find transaction using charge_id
        transaction = db.query(Transaction).filter(
            Transaction.charge_id == charge_id  # Using charge_id instead of payment_id
        ).first()

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Update status
        transaction.payment_status = charge["status"]

        # Update slot status if payment successful
        if charge["status"] == "successful":
            slot = db.query(Slot).filter(Slot.id == transaction.slot_id).first()
            if slot:
                slot.is_available = False  # Keep locked until item is collected

        db.commit()

        return {
            "success": True,
            "status": charge["status"],
            "paid": charge["paid"],
            "amount": charge["amount"] / 100
        }

    except Exception as e:
        print("Error in check_payment_status:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def handle_webhook(payload: Dict, db: Session = Depends(get_db)):
    try:
        event_data = payload.get("data", {})
        charge_id = event_data.get("id")
        status = event_data.get("status")

        if not charge_id:
            raise HTTPException(status_code=400, detail="Missing charge ID")

        # Find transaction using charge_id
        transaction = db.query(Transaction).filter(
            Transaction.charge_id == charge_id  # Using charge_id instead of payment_id
        ).first()

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Update status
        transaction.payment_status = status

        # Handle successful payment
        if status == "successful":
            slot = db.query(Slot).filter(Slot.id == transaction.slot_id).first()
            if slot:
                slot.is_available = False  # Keep locked until item is collected

        # Create API event record
        api_event = APIEvent(
            transaction_id=transaction.id,
            event_type="charge.complete",
            payload=payload
        )

        db.add(api_event)
        db.commit()

        return {"success": True, "message": "Webhook processed successfully"}

    except Exception as e:
        print("Error in webhook:", str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
