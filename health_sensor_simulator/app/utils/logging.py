"""Define logging related utility functions and classes."""
import logging
from http import HTTPStatus
from fastapi import Request, Response

request_msg_format = "%s:%d - \"%s\" %s - %.2fms"


def get_request_msg_args(request: Request, response: Response,
                         process_time: float) -> tuple:
    """Format the message for processing a http request.

    Args:
        request (Request): http request.
        response (Response): the corresponding response to the request.
        process_time (float): process time for the http request.

    Returns:
        tuple: the requisite args to format the message
    """
    try:
        response_status = HTTPStatus(response.status_code)
        status = f"{response_status.value} {response_status.phrase}"
    except ValueError:
        status = f"{response.status_code} Unknown Error"
    method_path = f"{request.method} {request.url.path} HTTP/{request.scope['http_version']}"
    args = (request.client.host, request.client.port,  # type: ignore
            method_path, status, process_time)
    return args


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


