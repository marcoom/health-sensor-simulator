"""Main function for running the integrated Health Sensor Simulator service.

This module provides the main entrypoint for the Health Sensor Simulator,
running both FastAPI and Streamlit services in parallel threads.
"""

import logging
import logging.config
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import NoReturn

import uvicorn
from fastapi import FastAPI

from src.app.config import get_settings
from src.app.api.routes import base_router as api_router

# Create FastAPI app
app = FastAPI(title="Health Sensor Simulator")
settings = get_settings()

# Configure logging
logging.config.dictConfig(settings.get_logging_config())
logger = logging.getLogger("src")

# Log startup message
logger.info(f"Starting {settings.PROJECT_NAME} with log level: {settings.LOG_LEVEL}")
logger.info(f"ANOMALY_DETECTION_METHOD: {settings.ANOMALY_DETECTION_METHOD}")
logger.info(f"ALARM_ENDPOINT_URL: {settings.ALARM_ENDPOINT_URL}")

# Include routers
app.include_router(api_router, prefix="/api/v1")


def run_fastapi_server() -> None:
    """Run the FastAPI server in a separate thread.
    
    This function starts the FastAPI server using uvicorn with the configured
    host and port settings. It runs indefinitely until the process is terminated.
    """
    logger.info(f"Starting FastAPI server on {settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}")
    uvicorn.run(
        "src.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=False,
        log_config=None  # Use our custom logging configuration
    )


def run_streamlit_app() -> None:
    """Run the Streamlit app as a subprocess in a separate thread.
    
    This function starts the Streamlit UI application using subprocess to ensure
    proper isolation from the FastAPI server. It runs indefinitely until terminated.
    """
    logger.info(f"Starting Streamlit app on {settings.STREAMLIT_HOST}:{settings.STREAMLIT_PORT}")
    
    # Construct path to the Streamlit application
    current_dir = Path(__file__).parent
    streamlit_app_path = current_dir / "app" / "ui" / "streamlit_app.py"
    
    # Build command to run Streamlit with configured parameters
    command = [
        sys.executable, "-m", "streamlit", "run",
        str(streamlit_app_path),
        "--server.address", settings.STREAMLIT_HOST,
        "--server.port", str(settings.STREAMLIT_PORT),
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Streamlit process failed with error: {e}")
    except KeyboardInterrupt:
        logger.info("Streamlit process interrupted by user")


def main() -> NoReturn:
    """Main entrypoint that starts both FastAPI and Streamlit services.
    
    This function initializes and starts both the FastAPI server and Streamlit UI
    in separate daemon threads, then monitors their health and handles graceful shutdown.
    
    Raises:
        KeyboardInterrupt: When user interrupts with Ctrl+C
        Exception: For any other errors during execution
    """
    logger.info("Starting Health Sensor Simulator - Integrated Mode")
    logger.info(f"FastAPI will be available at: http://{settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}")
    logger.info(f"Streamlit UI will be available at: http://{settings.STREAMLIT_HOST}:{settings.STREAMLIT_PORT}")
    
    # Start FastAPI server in a separate daemon thread
    fastapi_thread = threading.Thread(
        target=run_fastapi_server, 
        daemon=True, 
        name="FastAPI-Thread"
    )
    fastapi_thread.start()
    logger.info(f"FastAPI thread started: {fastapi_thread.name}")
    
    # Start Streamlit UI in a separate daemon thread
    streamlit_thread = threading.Thread(
        target=run_streamlit_app, 
        daemon=True, 
        name="Streamlit-Thread"
    )
    streamlit_thread.start()
    logger.info(f"Streamlit thread started: {streamlit_thread.name}")
    
    # Allow services time to initialize
    startup_delay = 3
    time.sleep(startup_delay)
    
    # Monitor thread health and handle shutdown
    try:
        logger.info("Both services started successfully. Press Ctrl+C to shutdown.")
        # Keep main thread alive by monitoring service thread status
        while fastapi_thread.is_alive() and streamlit_thread.is_alive():
            time.sleep(1)
        
        # If we reach here, one of the threads died unexpectedly
        logger.error("One or more service threads terminated unexpectedly")
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Unexpected error in main thread: {e}")
        raise
    finally:
        logger.info("Health Sensor Simulator shutdown complete")


if __name__ == "__main__":
    main()
