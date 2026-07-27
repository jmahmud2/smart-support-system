"""
Error handling utilities for consistent error responses.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Union
import traceback
import os


class AppException(Exception):
    """Custom application exception."""
    def __init__(self, message: str, status_code: int = 400, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


def handle_exception(exc: Exception, request: Request) -> JSONResponse:
    """Handle exceptions and return consistent JSON responses."""
    
    print(f"Error: {exc}")
    print(traceback.format_exc())
    
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.message,
                "details": exc.details,
                "path": str(request.url)
            }
        )
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "path": str(request.url)
            }
        )
    
    if hasattr(exc, "errors"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "message": "Validation error",
                "details": exc.errors(),
                "path": str(request.url)
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An internal server error occurred",
            "path": str(request.url),
            "debug": os.getenv("DEBUG", "False").lower() == "true" and str(exc)
        }
    )