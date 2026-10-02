from pydantic import BaseModel, Field

from fg_core.models.fluid_event import FluidEvent, FluidEventSchema


class EstimateRequest(BaseModel):
    fluid_event_id: str = Field(min_length=1)


class HiddenFluidEstimate(BaseModel):
    fluid_event_id: str
    hidden_fluid_ml: int
    method: str


__all__ = ["EstimateRequest", "FluidEvent", "FluidEventSchema", "HiddenFluidEstimate"]
