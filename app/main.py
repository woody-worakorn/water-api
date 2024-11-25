from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uuid
from .routes import payment_router, slots_router
from starlette.middleware.base import BaseHTTPMiddleware
import logging

# Import from relative paths
from .database import get_db, engine
from . import models, schemas

from .routes import payment

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Water Vending Machine API")

# Broader CORS settings
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Enhanced Ngrok middleware with logging
class NgrokMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log headers for debugging
        logger.debug(f"Request headers: {request.headers}")

        # Handle ngrok headers
        if "x-forwarded-proto" in request.headers:
            request.scope["scheme"] = request.headers["x-forwarded-proto"]

        # Add required headers for ngrok
        response = await call_next(request)
        response.headers["ngrok-skip-browser-warning"] = "true"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

# Debug middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.debug(f"Incoming request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.debug(f"Response status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

app.add_middleware(NgrokMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add error handler for network issues
@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(payment_router, prefix="/api", tags=["payment"])
app.include_router(slots_router, prefix="/api", tags=["slots"])

# Health check endpoint
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Try to make a simple query
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get all machines
@app.get("/machines/", response_model=List[schemas.Machine])
def get_machines(db: Session = Depends(get_db)):
    return db.query(models.VendingMachine).all()

# Get machine slots
@app.get("/machines/{machine_id}/slots", response_model=List[schemas.Slot])
def get_machine_slots(machine_id: str, db: Session = Depends(get_db)):
    return db.query(models.Slot).filter(models.Slot.machine_id == machine_id).all()

# Create new machine
@app.post("/machines/", response_model=schemas.Machine)
def create_machine(machine: schemas.MachineCreate, db: Session = Depends(get_db)):
    db_machine = models.VendingMachine(
        id=uuid.uuid4(),
        location=machine.location,
        status=machine.status
    )
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

# Initialize slots for a machine
@app.post("/machines/{machine_id}/slots/init", response_model=List[schemas.Slot])
def init_machine_slots(
    machine_id: str,
    db: Session = Depends(get_db)
):
    slots = []
    for row in range(1, 6):  # 5 rows
        for col in range(1, 7):  # 6 columns
            slot = models.Slot(
                id=uuid.uuid4(),
                machine_id=machine_id,
                row=row,
                column=col,
                product_name="Water Bottle",
                price=20.0,
                is_available=True
            )
            slots.append(slot)

    db.add_all(slots)
    db.commit()

    for slot in slots:
        db.refresh(slot)

    return slots
