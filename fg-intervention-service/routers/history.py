from fastapi import APIRouter

router = APIRouter(prefix="/intervention", tags=["intervention"])


@router.get("/{user_id}/history")
def get_history(user_id: str) -> dict[str, object]:
    """Placeholder until decisions and actions are associated with a user."""
    return {
        "user_id": user_id,
        "history": [],
        "message": "User-scoped intervention history is not yet available.",
    }
