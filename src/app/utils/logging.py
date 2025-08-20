"""Define logging related utility functions and classes."""
import logging


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with standardized configuration.
    
    This function is thread-safe and can be used in both FastAPI and Streamlit contexts.
    The logger configuration should be set up at the application level.
    
    Args:
        name: Name for the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StandardFormatter(logging.Formatter):
    """Logging Formatter to count warning / errors"""
    msg_format = "%(asctime)-22.19s %(name)-21s [%(levelname)s]:    " \
                 "%(message)s    (%(filename)s:%(lineno)d)"

    def build_msg_format(self, *args, **kwargs) -> str:
        """Wrapper function for building message customized format.

        Returns:
            str: log message format.
        """
        return self.msg_format

    def format(self, record: logging.LogRecord) -> str:
        """Format the given record to a log message.

        Args:
            record (logging.LogRecord): log record to format a log message.

        Returns:
            str: formatted log message.
        """
        log_fmt = self.build_msg_format(record)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


