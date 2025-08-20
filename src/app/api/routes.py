"""API endpoints for health sensor simulator."""
from typing import Any
from fastapi import APIRouter, HTTPException
from src.app.api.schemas import VersionResponse, VitalsResponse
from src.app.version import __version__
from src.app.services.data_simulator import get_stored_health_point

base_router = APIRouter()


@base_router.get("/version", response_model=VersionResponse)
async def version() -> Any:
    """Provide version information about the web service.

    \f
    Returns:
        VersionResponse: A json response containing the version number.
    """
    return VersionResponse(version=__version__)

@base_router.get("/vitals", response_model=VitalsResponse)
async def vitals() -> VitalsResponse:
    """Get the current vitals data from the health sensor simulator.
    
    Returns the last "sensed" values from health variables with timestamp.
    Uses the same data generation logic as the Streamlit interface.
    
    Returns:
        VitalsResponse: Current health vitals with UTC timestamp
        
    Raises:
        HTTPException: 500 if data generation fails
    """
    try:
        # Get the stored health point from shared memory (same as Streamlit UI)
        health_point = get_stored_health_point()
        
        # Convert parameter names to response field names and ensure proper types
        return VitalsResponse(
            heart_rate=int(round(health_point["heart_rate"])),
            oxygen_saturation=int(round(health_point["oxygen_saturation"])),
            breathing_rate=int(round(health_point["breathing_rate"])),
            systolic_bp=int(round(health_point["blood_pressure_systolic"])),
            diastolic_bp=int(round(health_point["blood_pressure_diastolic"])),
            body_temperature=round(health_point["body_temperature"], 1)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate health vitals: {str(e)}"
        )

