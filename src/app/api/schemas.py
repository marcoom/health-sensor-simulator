"""Define response model for the endpoint version."""
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Dict


class VersionResponse(BaseModel):
    """Response for version endpoint."""
    version: str = Field(..., example="1.0.0")

class VitalsResponse(BaseModel):
    """Response for vitals endpoint."""
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    heart_rate: int
    oxygen_saturation: int
    breathing_rate: int
    systolic_bp: int
    diastolic_bp: int
    body_temperature: float

class AnomalyResponse(BaseModel):
    """Response for anomaly detection endpoint."""
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    anomaly_score: float
    vitals: Dict[str, float] = Field(..., description="Health parameter values at time of anomaly")