from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors."""
    def __init__(self, message: str, details: str = None):
        self.message = message
        self.details = details
        super().__init__(self.message)

class BatchProcessingError(Exception):
    """Custom exception for batch processing errors."""
    def __init__(self, message: str, failed_items: list = None):
        self.message = message
        self.failed_items = failed_items or []
        super().__init__(self.message)

class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    def __init__(self, message: str, filename: str = None):
        self.message = message
        self.filename = filename
        super().__init__(self.message)

async def pdf_processing_exception_handler(request: Request, exc: PDFProcessingError):
    """Handle PDF processing errors."""
    logger.error(f"PDF processing error: {exc.message}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "PDF Processing Error",
            "message": exc.message,
            "details": exc.details,
            "type": "pdf_processing_error"
        }
    )

async def batch_processing_exception_handler(request: Request, exc: BatchProcessingError):
    """Handle batch processing errors."""
    logger.error(f"Batch processing error: {exc.message}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Batch Processing Error",
            "message": exc.message,
            "failed_items": exc.failed_items,
            "type": "batch_processing_error"
        }
    )

async def file_validation_exception_handler(request: Request, exc: FileValidationError):
    """Handle file validation errors."""
    logger.error(f"File validation error: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "File Validation Error",
            "message": exc.message,
            "filename": exc.filename,
            "type": "file_validation_error"
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "type": "http_error"
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "type": "validation_error"
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "type": "internal_error"
        }
    )

def setup_exception_handlers(app: FastAPI):
    """Setup all exception handlers."""
    app.add_exception_handler(PDFProcessingError, pdf_processing_exception_handler)
    app.add_exception_handler(BatchProcessingError, batch_processing_exception_handler)
    app.add_exception_handler(FileValidationError, file_validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
