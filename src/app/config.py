"""Base settings class contains only important fields."""
# mypy: ignore-errors
from typing import Dict, Literal
from pydantic import BaseModel, BaseSettings
from src.app.utils.logging import StandardFormatter


class LoggingConfig(BaseModel):
    version: int
    disable_existing_loggers: bool = False
    formatters: Dict
    handlers: Dict
    loggers: Dict


class Settings(BaseSettings):
    PROJECT_NAME: str = 'Health Sensor Simulator'
    PROJECT_SLUG: str = 'health_sensor_simulator'

    DEBUG: bool = True
    API_STR: str = "/api/v1"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING"] = "INFO"
    
    # Data generation settings
    DATA_GENERATION_INTERVAL_SECONDS: int = 5
    
    # Server configuration
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    STREAMLIT_HOST: str = "0.0.0.0"
    STREAMLIT_PORT: int = 8501

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration based on LOG_LEVEL setting."""
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                'standardFormatter': {'()': StandardFormatter},
            },
            "handlers": {
                'consoleHandler': {
                    'class': 'logging.StreamHandler',
                    'level': self.LOG_LEVEL,
                    'formatter': 'standardFormatter',
                    'stream': 'ext://sys.stdout',
                },
            },
            "loggers": {
                "src": {
                    'handlers': ['consoleHandler'],
                    'level': self.LOG_LEVEL,
                },
                "uvicorn": {
                    'handlers': ['consoleHandler']
                },
                "uvicorn.access": {
                    # Use the project logger to replace uvicorn.access logger
                    'handlers': []
                }
            }
        }

    class Config:
        case_sensitive = True


def get_settings() -> Settings:
    """Return an instance of the Settings class.
    
    This function is used to get the application settings in a way that's compatible
    with FastAPI's dependency injection system.
    
    Returns:
        Settings: An instance of the Settings class.
    """
    return Settings()
