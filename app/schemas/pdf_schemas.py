from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime

class PDFPageSchema(BaseModel):
    """Schema for a single PDF page."""
    page_number: int = Field(..., ge=1, description="Page number")
    text: str = Field(..., description="Extracted text from the page")
    text_length: int = Field(..., ge=0, description="Length of extracted text")
    tables: List[List[List[str]]] = Field(default=[], description="Extracted tables")
    bbox: Optional[List[float]] = Field(None, description="Page bounding box")
    width: Optional[float] = Field(None, ge=0, description="Page width")
    height: Optional[float] = Field(None, ge=0, description="Page height")
    error: Optional[str] = Field(None, description="Error message if processing failed")

class PDFProcessingResultSchema(BaseModel):
    """Schema for PDF processing result."""
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    processed_at: str = Field(..., description="Processing timestamp")
    pages: List[PDFPageSchema] = Field(..., description="Processed pages")
    total_pages: int = Field(..., ge=0, description="Total number of pages")
    total_text_length: int = Field(..., ge=0, description="Total text length")
    metadata: Dict[str, Any] = Field(default={}, description="PDF metadata")
    file_hash: str = Field(..., description="SHA-256 hash of the file")
    status: str = Field(..., description="Processing status")

class BatchProcessingSummarySchema(BaseModel):
    """Schema for batch processing summary."""
    success_count: int = Field(..., ge=0, description="Number of successfully processed files")
    error_count: int = Field(..., ge=0, description="Number of failed files")
    total_pages: int = Field(..., ge=0, description="Total pages processed")
    total_text_length: int = Field(..., ge=0, description="Total text length")

class BatchProcessingResultSchema(BaseModel):
    """Schema for batch processing result."""
    batch_id: str = Field(..., description="Unique batch identifier")
    processed_at: str = Field(..., description="Processing timestamp")
    total_files: int = Field(..., ge=1, description="Total number of files in batch")
    successful: List[PDFProcessingResultSchema] = Field(..., description="Successfully processed files")
    failed: List[Dict[str, Any]] = Field(..., description="Failed files with error details")
    summary: BatchProcessingSummarySchema = Field(..., description="Batch processing summary")

class TextSearchMatchSchema(BaseModel):
    """Schema for text search match."""
    position: int = Field(..., ge=0, description="Position of match in text")
    context: str = Field(..., description="Context around the match")
    match_text: str = Field(..., description="Actual matched text")

class PageSearchResultSchema(BaseModel):
    """Schema for page search result."""
    page_number: int = Field(..., ge=1, description="Page number")
    matches: List[TextSearchMatchSchema] = Field(..., description="Matches found on this page")
    match_count: int = Field(..., ge=0, description="Number of matches on this page")

class TextSearchResultSchema(BaseModel):
    """Schema for text search result."""
    query: str = Field(..., description="Search query")
    matches: List[PageSearchResultSchema] = Field(..., description="Pages with matches")
    total_matches: int = Field(..., ge=0, description="Total number of matches")
    pages_with_matches: int = Field(..., ge=0, description="Number of pages with matches")

class PDFSummarySchema(BaseModel):
    """Schema for PDF summary."""
    filename: str = Field(..., description="Filename")
    total_pages: int = Field(..., ge=0, description="Total pages")
    total_text_length: int = Field(..., ge=0, description="Total text length")
    average_page_length: float = Field(..., ge=0, description="Average page text length")
    longest_page: int = Field(..., ge=0, description="Length of longest page")
    shortest_page: int = Field(..., ge=0, description="Length of shortest page")
    pages_with_tables: int = Field(..., ge=0, description="Number of pages with tables")
    total_tables: int = Field(..., ge=0, description="Total number of tables")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    processed_at: Optional[str] = Field(None, description="Processing timestamp")
    metadata: Dict[str, Any] = Field(default={}, description="PDF metadata")

# Request schemas
class TextSearchRequestSchema(BaseModel):
    """Schema for text search request."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty or whitespace only')
        return v.strip()

class BatchUploadRequestSchema(BaseModel):
    """Schema for batch upload request."""
    files: List[str] = Field(..., min_items=1, max_items=10, description="List of file paths or names")
    
    @validator('files')
    def validate_files(cls, v):
        if not v:
            raise ValueError('At least one file must be provided')
        return v

# Response schemas
class APIResponseSchema(BaseModel):
    """Base API response schema."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Response timestamp")

class ErrorResponseSchema(BaseModel):
    """Error response schema."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Additional error details")
    type: str = Field(..., description="Error type identifier")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Error timestamp")
