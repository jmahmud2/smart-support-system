import logging
import sys
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger

def log_request(logger: logging.Logger, method: str, path: str, extra: dict = None):
    extra_str = f" | {extra}" if extra else ""
    logger.info(f"REQUEST: {method} {path}{extra_str}")

def log_response(logger: logging.Logger, status: int, duration: float = None, extra: dict = None):
    emoji = "✅" if status < 400 else "❌" if status < 500 else "🔥"
    duration_str = f" ({duration:.2f}s)" if duration else ""
    extra_str = f" | {extra}" if extra else ""
    logger.info(f"{emoji} RESPONSE: {status}{duration_str}{extra_str}")

def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    import traceback
    logger.error(f"ERROR: {context} - {str(error)}")
    logger.error(traceback.format_exc())

def log_workflow_step(logger: logging.Logger, step: str, data: dict = None):
    data_str = f" | {data}" if data else ""
    logger.info(f"WORKFLOW: {step}{data_str}")