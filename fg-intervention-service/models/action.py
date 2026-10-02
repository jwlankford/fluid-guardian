from pydantic import BaseModel, Field

from fg_core.models.action import Action, ActionSchema


class ActRequest(BaseModel):
    decision_id: str = Field(min_length=1)
    action_type: str = Field(min_length=1, max_length=100)


class ActionResponse(BaseModel):
    action: ActionSchema
    message: str


__all__ = ["ActRequest", "Action", "ActionResponse", "ActionSchema"]
