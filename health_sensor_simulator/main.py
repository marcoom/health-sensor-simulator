"""Main function for running the API service."""
# mypy: ignore-errors
import logging
import logging.config
from fastapi import FastAPI
import uvicorn

# Import using absolute imports
from health_sensor_simulator.app.config import get_settings

# Create FastAPI app
app = FastAPI(title="Health Sensor Simulator")
settings = get_settings()

# Configure logging
logging.config.dictConfig(settings.get_logging_config())
logger = logging.getLogger("health_sensor_simulator")

# Log startup message
logger.info(f"Starting {settings.PROJECT_NAME} with log level: {settings.LOG_LEVEL}")

# Import and include routers
from health_sensor_simulator.app.api.routes import base_router as api_router
app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("health_sensor_simulator.main:app", host="0.0.0.0", port=8080, reload=False)  # nosec
