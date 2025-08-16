"""Define logging related utility functions and classes."""
import logging




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


