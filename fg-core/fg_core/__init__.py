"""Shared models and utilities for Fluid Guardian services."""

from fg_core.db import SessionLocal, configure_database, create_all, get_session, session_scope
from fg_core.models import (
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
)
from fg_core.utils import generate_id, utc_now

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
    "SessionLocal",
    "configure_database",
    "create_all",
    "generate_id",
    "get_session",
    "session_scope",
    "utc_now",
]
