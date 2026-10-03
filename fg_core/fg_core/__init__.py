"""Shared models and utilities for Fluid Guardian services."""

from .db import SessionLocal, configure_database, create_all, get_session, session_scope
from .models import (
    Action,
    ActionSchema,
    BehaviorProfile,
    BehaviorProfileSchema,
    Decision,
    DecisionSchema,
    Escalation,
    EscalationSchema,
    FluidEvent,
    FluidEventSchema,
    Prediction,
    PredictionSchema,
    UserAccount,
    UserAccountSchema,
)
from .utils import generate_id, utc_now

__all__ = [
    "Action",
    "ActionSchema",
    "BehaviorProfile",
    "BehaviorProfileSchema",
    "Decision",
    "DecisionSchema",
    "Escalation",
    "EscalationSchema",
    "FluidEvent",
    "FluidEventSchema",
    "Prediction",
    "PredictionSchema",
    "UserAccount",
    "UserAccountSchema",
    "SessionLocal",
    "configure_database",
    "create_all",
    "generate_id",
    "get_session",
    "session_scope",
    "utc_now",
]
