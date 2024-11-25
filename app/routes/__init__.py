# app/routes/__init__.py
from .payment import router as payment_router
from .slots import router as slots_router

__all__ = ["payment_router", "slots_router"]
