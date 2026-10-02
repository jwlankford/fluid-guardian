from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.behavior_profile import BehaviorProfile
from fg_core.models.behavior_profile import BehaviorProfileSchema

router = APIRouter(prefix="/learning", tags=["learning"])


@router.get("/{user_id}/profile", response_model=BehaviorProfileSchema)
def get_profile(user_id: str, db: Session = Depends(get_session)):
    profile = db.scalar(
        select(BehaviorProfile).where(BehaviorProfile.subject_id == user_id)
    )
    if profile is None:
        raise HTTPException(status_code=404, detail="Behavior profile not found")
    return profile
