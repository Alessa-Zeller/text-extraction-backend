from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
from pathlib import Path
import tempfile
import asyncio

from app.core.security import get_current_user
from app.core.config import settings
from app.services.pdf_service import pdf_processor
from app.schemas.pdf_schemas import (
    PDFProcessingResultSchema,
    BatchProcessingResultSchema,
    TextSearchResultSchema,
    TextSearchRequestSchema,
    PDFSummarySchema,
    APIResponseSchema
)
from app.core.exceptions import PDFProcessingError, BatchProcessingError, FileValidationError

router = APIRouter()

@router.post("/upload", response_model=APIResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_and_process_pdf(
    file: UploadFile = File(..., description="PDF file to process"),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process a single PDF file."""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = Path(temp_file.name)
        
        # Process the PDF (clinical data only)
        result = await pdf_processor.process_single_pdf_clinical_only(temp_file_path)
        
        # Add user context to result
        result["processed_by"] = current_user["user_id"]
        
        return APIResponseSchema(
            success=True,
            message="PDF processed successfully",
            data=result
        )
        
    except FileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File validation error: {e.message}"
        )
    except PDFProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"PDF processing error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file and Path(temp_file.name).exists():
            os.unlink(temp_file.name)

@router.post("/batch-upload", response_model=APIResponseSchema, status_code=status.HTTP_201_CREATED)
async def batch_upload_and_process_pdfs(
    files: List[UploadFile] = File(..., description="List of PDF files to process"),
    current_user: dict = Depends(get_current_user)
):
    """Upload and process multiple PDF files in batch."""
    
    if len(files) > settings.BATCH_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Batch size exceeds maximum allowed size of {settings.BATCH_SIZE}"
        )
    
    # Validate all files are PDFs
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File {file.filename} is not a PDF. Only PDF files are allowed."
            )
    
    temp_files = []
    try:
        # Create temporary files
        temp_file_paths = []
        for file in files:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            shutil.copyfileobj(file.file, temp_file)
            temp_file.close()
            temp_file_path = Path(temp_file.name)
            temp_file_paths.append(temp_file_path)
            temp_files.append(temp_file.name)
        
        # Process the batch (clinical data only)
        result = await pdf_processor.process_batch_pdfs_clinical_only(temp_file_paths)
        
        # Add user context to result
        result["processed_by"] = current_user["user_id"]
        
        return APIResponseSchema(
            success=True,
            message=f"Batch processing completed. {result['summary']['success_count']} files processed successfully, {result['summary']['error_count']} failed. Clinical data extracted from {result['summary']['clinical_data_extracted']} files.",
            data=result
        )
        
    except BatchProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Batch processing error: {e.message}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
    finally:
        # Clean up temporary files
        for temp_file_name in temp_files:
            if os.path.exists(temp_file_name):
                os.unlink(temp_file_name)

@router.post("/search", response_model=APIResponseSchema)
async def search_text_in_pdf_results(
    search_request: TextSearchRequestSchema,
    pdf_results: PDFProcessingResultSchema,
    current_user: dict = Depends(get_current_user)
):
    """Search for text within PDF processing results."""
    
    try:
        # Convert Pydantic model to dict for processing
        results_dict = pdf_results.dict()
        
        # Perform search
        search_results = pdf_processor.search_text_in_results(
            results_dict, 
            search_request.query
        )
        
        return APIResponseSchema(
            success=True,
            message=f"Search completed. Found {search_results['total_matches']} matches.",
            data=search_results
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search error: {str(e)}"
        )

@router.post("/summary", response_model=APIResponseSchema)
async def get_pdf_summary(
    pdf_results: PDFProcessingResultSchema,
    current_user: dict = Depends(get_current_user)
):
    """Generate a summary of PDF processing results."""
    
    try:
        # Convert Pydantic model to dict for processing
        results_dict = pdf_results.dict()
        
        # Generate summary
        summary = pdf_processor.get_pdf_summary(results_dict)
        
        return APIResponseSchema(
            success=True,
            message="Summary generated successfully",
            data=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation error: {str(e)}"
        )

@router.get("/health", response_model=APIResponseSchema)
async def pdf_service_health():
    """Check PDF service health."""
    return APIResponseSchema(
        success=True,
        message="PDF service is healthy",
        data={
            "service": "pdf_processor",
            "status": "healthy",
            "max_batch_size": settings.BATCH_SIZE,
            "max_file_size": settings.MAX_FILE_SIZE,
            "allowed_file_types": settings.ALLOWED_FILE_TYPES
        }
    )

# Admin-only endpoints
@router.get("/stats", response_model=APIResponseSchema)
async def get_processing_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get PDF processing statistics (admin only)."""
    
    # Check admin privileges
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # In a real application, you would fetch these from a database
    stats = {
        "total_files_processed": 0,
        "total_pages_processed": 0,
        "total_text_extracted": 0,
        "average_processing_time": 0,
        "success_rate": 100.0,
        "most_common_errors": [],
        "service_uptime": "N/A - Mock data"
    }
    
    return APIResponseSchema(
        success=True,
        message="Processing statistics retrieved successfully",
        data=stats
    )
