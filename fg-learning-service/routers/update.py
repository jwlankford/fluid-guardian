from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fg_core.db.session import get_session
from fg_core.models.behavior_profile import BehaviorProfile
from models.behavior_profile import LearningUpdateRequest, LearningUpdateResponse
from utils.hotspot_analysis import detect_risk_hotspots
from utils.pattern_detection import detect_evening_intake_pattern
from utils.response_rate import compute_notification_response_rate

router = APIRouter(prefix="/learning", tags=["learning"])


@router.post("/update", response_model=LearningUpdateResponse)
def update_profile(request: LearningUpdateRequest, db: Session = Depends(get_session)):
    if request.notification_responses > request.notification_count:
        raise HTTPException(
            status_code=422,
            detail="notification_responses cannot exceed notification_count",
        )
    evening_pattern = detect_evening_intake_pattern(request.recent_events)
    response_rate = compute_notification_response_rate(
        request.notification_responses, request.notification_count
    )
    hotspots = detect_risk_hotspots(request.recent_events)
    profile = db.scalar(
        select(BehaviorProfile).where(BehaviorProfile.subject_id == request.user_id)
    )
    attributes = {
        "evening_intake_pattern": evening_pattern,
        "notification_response_rate": response_rate,
        "risk_hotspots": hotspots,
    }
    if profile is None:
        profile = BehaviorProfile(subject_id=request.user_id, profile=attributes)
        db.add(profile)
    else:
        profile.profile = {**profile.profile, **attributes}
    db.commit()
    db.refresh(profile)
    return LearningUpdateResponse(
        profile=profile,
        evening_intake_pattern=evening_pattern,
        notification_response_rate=response_rate,
        risk_hotspots=hotspots,
    )
