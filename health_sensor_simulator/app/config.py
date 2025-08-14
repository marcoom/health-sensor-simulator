"""Base settings class contains only important fields."""
# mypy: ignore-errors
from typing import Dict, Literal
from pydantic import BaseModel, BaseSettings
from health_sensor_simulator.app.utils.logging import StandardFormatter


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
                "health_sensor_simulator": {
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
