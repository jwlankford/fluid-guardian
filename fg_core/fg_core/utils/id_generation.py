"""Identifier generation helpers."""

from uuid import uuid4


def generate_id() -> str:
    """Return a new UUID4 identifier as a string."""
    return str(uuid4())
