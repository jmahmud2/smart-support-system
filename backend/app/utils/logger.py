"""
Logging utility for the Smart Support System.
Provides consistent logging across the application.
"""

import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: The module name (usually __name__)
    
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)


def log_request(logger: logging.Logger, method: str, path: str, data: dict = None):
    """Log an incoming API request."""
    logger.info(f"📥 REQUEST: {method} {path}")
    if data:
        # Truncate long data for readability
        safe_data = {}
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 100:
                safe_data[key] = value[:100] + "..."
            else:
                safe_data[key] = value
        logger.debug(f"   Data: {safe_data}")


def log_response(logger: logging.Logger, status: int, duration: float = None):
    """Log an API response."""
    emoji = "✅" if status < 400 else "❌" if status < 500 else "🔥"
    duration_str = f" ({duration:.2f}s)" if duration else ""
    logger.info(f"{emoji} RESPONSE: {status}{duration_str}")


def log_error(logger: logging.Logger, error: Exception, context: str = ""):
    """Log an error with full traceback."""
    import traceback
    logger.error(f"💥 ERROR: {context} - {str(error)}")
    logger.error(traceback.format_exc())


def log_workflow_step(logger: logging.Logger, step: str, data: dict = None):
    """Log a workflow step execution."""
    logger.info(f"⚙️ WORKFLOW: {step}")
    if data:
        logger.debug(f"   {data}")