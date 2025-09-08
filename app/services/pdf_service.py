import os
import asyncio
from typing import List, Dict, Any, Optional
from pathlib import Path
import pdfplumber
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from datetime import datetime
import re
"""
LlamaParse is an optional dependency used only when OCR/cloud parsing is enabled.
We avoid importing it at module import time to prevent startup failures if the
library (or its transitive deps like llama_index) is not installed.
"""

from app.core.config import settings
from app.core.exceptions import PDFProcessingError, BatchProcessingError, FileValidationError

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF processing service with batch processing capabilities."""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(exist_ok=True)
        self.executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_TASKS)
    
    def validate_file(self, file_path: Path, filename: str = None) -> None:
        """Validate PDF file."""
        if not file_path.exists():
            raise FileValidationError(f"File not found", filename)
        
        if file_path.stat().st_size > settings.MAX_FILE_SIZE:
            raise FileValidationError(
                f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes",
                filename
            )
        
        if file_path.suffix.lower() not in settings.ALLOWED_FILE_TYPES:
            raise FileValidationError(
                f"File type not allowed. Allowed types: {settings.ALLOWED_FILE_TYPES}",
                filename
            )
    
    def extract_text_from_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from a single PDF file."""
        try:
            self.validate_file(file_path, file_path.name)
            
            # First try standard text extraction
            result = self._try_standard_extraction(file_path)
            
            # If no text was extracted (image-based PDF), use LlamaParse
            if result["total_text_length"] == 0:
                logger.info(f"No text found in {file_path.name}, attempting LlamaParse extraction")
                result = self._extract_text_with_llamaparse(file_path)
            
            return result
            
        except FileValidationError:
            raise
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise PDFProcessingError(
                f"Failed to process PDF: {str(e)}",
                details=f"File: {file_path.name}"
            )
    
    def _try_standard_extraction(self, file_path: Path) -> Dict[str, Any]:
        """Try standard PDF text extraction first."""
        result = {
            "filename": file_path.name,
            "file_size": file_path.stat().st_size,
            "processed_at": datetime.utcnow().isoformat(),
            "pages": [],
            "total_pages": 0,
            "total_text_length": 0,
            "metadata": {},
            "status": "success",
            "clinical_data": {}
        }
        
        with pdfplumber.open(file_path) as pdf:
            result["total_pages"] = len(pdf.pages)
            result["metadata"] = pdf.metadata or {}
            result["metadata"]["extraction_method"] = "standard"
            
            for page_num, page in enumerate(pdf.pages, 1):
                try:
                    text = page.extract_text() or ""
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    table_data = []
                    if tables:
                        for table in tables:
                            if table:  # Skip empty tables
                                table_data.append(table)
                    
                    page_info = {
                        "page_number": page_num,
                        "text": text,
                        "text_length": len(text),
                        "tables": table_data,
                        "bbox": page.bbox,
                        "width": page.width,
                        "height": page.height
                    }
                    
                    # Extract clinical data from any page with text
                    if text.strip() and not result.get("clinical_data"):
                        clinical_data = self._extract_clinical_data(text)
                        if clinical_data.get("patient_name", {}).get("full_name") or clinical_data.get("date_of_birth"):
                            result["clinical_data"] = clinical_data
                            page_info["clinical_data"] = clinical_data
                    
                    result["pages"].append(page_info)
                    result["total_text_length"] += len(text)
                    
                except Exception as e:
                    logger.warning(f"Error processing page {page_num}: {str(e)}")
                    result["pages"].append({
                        "page_number": page_num,
                        "text": "",
                        "text_length": 0,
                        "tables": [],
                        "error": str(e)
                    })
        
        # Generate file hash for deduplication
        result["file_hash"] = self._generate_file_hash(file_path)
        
        return result
    
    def _generate_file_hash(self, file_path: Path) -> str:
        """Generate SHA-256 hash of file for deduplication."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _extract_text_with_llamaparse(self, file_path: Path) -> Dict[str, Any]:
        """Extract text using LlamaParse (cloud parser with built-in OCR)."""
        try:
            if not settings.LLAMAPARSE_API_KEY:
                raise PDFProcessingError(
                    "LlamaParse API key is not configured. Set LLAMAPARSE_API_KEY in environment.",
                    details=f"File: {file_path.name}"
                )
            # Lazy import to avoid import errors at app startup when optional deps are missing
            from llama_parse import LlamaParse

            parser = LlamaParse(
                api_key=settings.LLAMAPARSE_API_KEY,
                result_type=settings.LLAMAPARSE_RESULT_TYPE or "text",
            )
            # LlamaParse returns a list of documents; each typically contains text content
            docs = parser.load_data(str(file_path))

            # Aggregate texts and approximate per-page segmentation
            pages: List[Dict[str, Any]] = []
            total_text_length = 0
            for idx, d in enumerate(docs, start=1):
                page_text = getattr(d, "text", None) or getattr(d, "page_content", "") or ""
                pages.append({
                    "page_number": idx,
                    "text": page_text,
                    "text_length": len(page_text),
                    "tables": [],
                })
                total_text_length += len(page_text)

            result: Dict[str, Any] = {
                "filename": file_path.name,
                "file_size": file_path.stat().st_size,
                "processed_at": datetime.utcnow().isoformat(),
                "pages": pages,
                "total_pages": len(pages),
                "total_text_length": total_text_length,
                "metadata": {"extraction_method": "LlamaParse"},
                "status": "success",
                "clinical_data": {}
            }

            # Try extracting clinical data from all pages (prioritize page 2, then page 1)
            clinical_data = {}
            if len(pages) >= 2:
                # Try page 2 first (index 1)
                text_p2 = pages[1].get("text", "")
                clinical_data = self._extract_clinical_data(text_p2)
                pages[1]["clinical_data"] = clinical_data
            elif len(pages) >= 1:
                # If only 1 page, use page 1 (index 0)
                text_p1 = pages[0].get("text", "")
                clinical_data = self._extract_clinical_data(text_p1)
                pages[0]["clinical_data"] = clinical_data
            
            result["clinical_data"] = clinical_data

            # Generate file hash for deduplication
            result["file_hash"] = self._generate_file_hash(file_path)
            return result

        except PDFProcessingError:
            raise
        except Exception as e:
            logger.error(f"Error processing PDF with LlamaParse {file_path}: {str(e)}")
            raise PDFProcessingError(
                f"Failed to process PDF with LlamaParse: {str(e)}",
                details=f"File: {file_path.name}"
            )
    
    def _extract_clinical_data(self, text: str) -> Dict[str, Any]:
        """Extract structured clinical data from text."""
        clinical_data = {
            "patient_name": {
                "first_name": None,
                "last_name": None,
                "full_name": None
            },
            "date_of_birth": None,
            "extraction_confidence": "medium"
        }
        
        if not text:
            return clinical_data
        
        # Convert to lowercase for pattern matching but preserve original case for extraction
        text_lower = text.lower()
        
        # Pattern for Patient Name extraction
        # Look for "Patient Name:" followed by name
        patient_name_patterns = [
            r'patient\s+name\s*:\s*([^\n\r]+)',
            r'patient\s*:\s*([^\n\r]+)',
            r'name\s*:\s*([^\n\r]+)'
        ]
        
        for pattern in patient_name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                full_name = text[match.start(1):match.end(1)].strip()
                clinical_data["patient_name"]["full_name"] = full_name
                
                # Try to split into first and last name
                name_parts = full_name.split()
                if len(name_parts) >= 2:
                    clinical_data["patient_name"]["first_name"] = name_parts[0]
                    clinical_data["patient_name"]["last_name"] = " ".join(name_parts[1:])
                elif len(name_parts) == 1:
                    clinical_data["patient_name"]["first_name"] = name_parts[0]
                
                break
        
        # Pattern for Date of Birth extraction
        dob_patterns = [
            r'dob\s*:\s*([^\n\r]+)',
            r'date\s+of\s+birth\s*:\s*([^\n\r]+)',
            r'birth\s+date\s*:\s*([^\n\r]+)',
            r'born\s*:\s*([^\n\r]+)'
        ]
        
        for pattern in dob_patterns:
            match = re.search(pattern, text_lower)
            if match:
                dob_text = text[match.start(1):match.end(1)].strip()
                # Clean up common OCR artifacts
                dob_text = re.sub(r'[^\d/\-\s]', '', dob_text)
                clinical_data["date_of_birth"] = dob_text
                break
        
        # Set confidence based on what was found
        found_items = sum([
            bool(clinical_data["patient_name"]["full_name"]),
            bool(clinical_data["date_of_birth"])
        ])
        
        if found_items == 2:
            clinical_data["extraction_confidence"] = "high"
        elif found_items == 1:
            clinical_data["extraction_confidence"] = "medium"
        else:
            clinical_data["extraction_confidence"] = "low"
        
        return clinical_data
    
    def extract_clinical_data_only(self, file_path: Path) -> Dict[str, Any]:
        """Extract only clinical data from PDF without full text content."""
        try:
            self.validate_file(file_path, file_path.name)
            
            # First try standard text extraction
            result = self._try_standard_extraction(file_path)
            
            # If no text was extracted (image-based PDF), use LlamaParse
            if result["total_text_length"] == 0:
                logger.info(f"No text found in {file_path.name}, attempting LlamaParse extraction")
                try:
                    result = self._extract_text_with_llamaparse(file_path)
                except ImportError as e:
                    logger.warning(f"LlamaParse not available: {str(e)}")
                    result["status"] = "partial_success"
                    result["message"] = "Image-based PDF detected. OCR service not available. Please install llama-parse for full text extraction."
                    result["metadata"]["extraction_method"] = "standard_no_ocr"
                except Exception as e:
                    logger.warning(f"LlamaParse extraction failed: {str(e)}")
                    result["status"] = "partial_success"
                    result["message"] = f"Image-based PDF detected. OCR extraction failed: {str(e)}"
                    result["metadata"]["extraction_method"] = "standard_ocr_failed"
            
            # Create lightweight response with only essential data
            clinical_response = {
                "filename": result["filename"],
                "file_size": result["file_size"],
                "processed_at": result["processed_at"],
                "total_pages": result["total_pages"],
                "extraction_method": result["metadata"].get("extraction_method", "unknown"),
                "clinical_data": result.get("clinical_data", {}),
                "file_hash": result["file_hash"],
                "status": result["status"],
                # Temporarily include extracted text for debugging (all pages combined)
                "debug_extracted_text": " ".join([page.get("text", "") for page in result.get("pages", [])])[:1000]
            }
            
            return clinical_response
            
        except FileValidationError:
            raise
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            raise PDFProcessingError(
                f"Failed to process PDF: {str(e)}",
                details=f"File: {file_path.name}"
            )
    
    async def process_single_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Process a single PDF asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.extract_text_from_pdf, 
            file_path
        )
    
    async def process_single_pdf_clinical_only(self, file_path: Path) -> Dict[str, Any]:
        """Process a single PDF asynchronously, returning only clinical data."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.extract_clinical_data_only, 
            file_path
        )
    
    async def process_batch_pdfs(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Process multiple PDFs in batch with concurrency control."""
        if not file_paths:
            raise BatchProcessingError("No files provided for batch processing")
        
        if len(file_paths) > settings.BATCH_SIZE:
            raise BatchProcessingError(
                f"Batch size exceeds maximum allowed size of {settings.BATCH_SIZE}"
            )
        
        batch_result = {
            "batch_id": hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()[:12],
            "processed_at": datetime.utcnow().isoformat(),
            "total_files": len(file_paths),
            "successful": [],
            "failed": [],
            "summary": {
                "success_count": 0,
                "error_count": 0,
                "total_pages": 0,
                "total_text_length": 0
            }
        }
        
        # Process files concurrently
        tasks = [self.process_single_pdf(file_path) for file_path in file_paths]
        
        try:
            for i, task in enumerate(asyncio.as_completed(tasks)):
                try:
                    result = await task
                    batch_result["successful"].append(result)
                    batch_result["summary"]["success_count"] += 1
                    batch_result["summary"]["total_pages"] += result["total_pages"]
                    batch_result["summary"]["total_text_length"] += result["total_text_length"]
                    
                except Exception as e:
                    error_info = {
                        "filename": file_paths[i].name if i < len(file_paths) else "unknown",
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    batch_result["failed"].append(error_info)
                    batch_result["summary"]["error_count"] += 1
                    logger.error(f"Failed to process {file_paths[i]}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            raise BatchProcessingError(
                f"Batch processing failed: {str(e)}",
                failed_items=[fp.name for fp in file_paths]
            )
        
        return batch_result
    
    async def process_batch_pdfs_clinical_only(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Process multiple PDFs in batch with concurrency control, returning only clinical data."""
        if not file_paths:
            raise BatchProcessingError("No files provided for batch processing")
        
        if len(file_paths) > settings.BATCH_SIZE:
            raise BatchProcessingError(
                f"Batch size exceeds maximum allowed size of {settings.BATCH_SIZE}"
            )
        
        batch_result = {
            "batch_id": hashlib.md5(str(datetime.utcnow()).encode()).hexdigest()[:12],
            "processed_at": datetime.utcnow().isoformat(),
            "total_files": len(file_paths),
            "successful": [],
            "failed": [],
            "summary": {
                "success_count": 0,
                "error_count": 0,
                "total_pages": 0,
                "clinical_data_extracted": 0
            }
        }
        
        # Process files concurrently
        tasks = [self.process_single_pdf_clinical_only(file_path) for file_path in file_paths]
        
        try:
            for i, task in enumerate(asyncio.as_completed(tasks)):
                try:
                    result = await task
                    batch_result["successful"].append(result)
                    batch_result["summary"]["success_count"] += 1
                    batch_result["summary"]["total_pages"] += result["total_pages"]
                    
                    # Count clinical data extractions
                    if result.get("clinical_data", {}).get("patient_name", {}).get("full_name") or result.get("clinical_data", {}).get("date_of_birth"):
                        batch_result["summary"]["clinical_data_extracted"] += 1
                    
                except Exception as e:
                    error_info = {
                        "filename": file_paths[i].name if i < len(file_paths) else "unknown",
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    batch_result["failed"].append(error_info)
                    batch_result["summary"]["error_count"] += 1
                    logger.error(f"Failed to process {file_paths[i]}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            raise BatchProcessingError(
                f"Batch processing failed: {str(e)}",
                failed_items=[fp.name for fp in file_paths]
            )
        
        return batch_result
    
    def search_text_in_results(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Search for text within processed PDF results."""
        if not query or not results.get("pages"):
            return {"matches": [], "total_matches": 0}
        
        matches = []
        query_lower = query.lower()
        
        for page in results["pages"]:
            if "text" in page and query_lower in page["text"].lower():
                # Find all occurrences in the page
                text_lower = page["text"].lower()
                start = 0
                page_matches = []
                
                while True:
                    pos = text_lower.find(query_lower, start)
                    if pos == -1:
                        break
                    
                    # Extract context around the match
                    context_start = max(0, pos - 100)
                    context_end = min(len(page["text"]), pos + len(query) + 100)
                    context = page["text"][context_start:context_end]
                    
                    page_matches.append({
                        "position": pos,
                        "context": context,
                        "match_text": page["text"][pos:pos + len(query)]
                    })
                    
                    start = pos + 1
                
                if page_matches:
                    matches.append({
                        "page_number": page["page_number"],
                        "matches": page_matches,
                        "match_count": len(page_matches)
                    })
        
        return {
            "query": query,
            "matches": matches,
            "total_matches": sum(page["match_count"] for page in matches),
            "pages_with_matches": len(matches)
        }
    
    def get_pdf_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the PDF processing results."""
        if not results or not results.get("pages"):
            return {"error": "No valid results to summarize"}
        
        # Calculate statistics
        page_lengths = [page.get("text_length", 0) for page in results["pages"]]
        
        summary = {
            "filename": results.get("filename", "Unknown"),
            "total_pages": results.get("total_pages", 0),
            "total_text_length": results.get("total_text_length", 0),
            "average_page_length": sum(page_lengths) / len(page_lengths) if page_lengths else 0,
            "longest_page": max(page_lengths) if page_lengths else 0,
            "shortest_page": min(page_lengths) if page_lengths else 0,
            "pages_with_tables": sum(1 for page in results["pages"] if page.get("tables")),
            "total_tables": sum(len(page.get("tables", [])) for page in results["pages"]),
            "file_size": results.get("file_size", 0),
            "processed_at": results.get("processed_at"),
            "metadata": results.get("metadata", {})
        }
        
        return summary

# Global PDF processor instance
pdf_processor = PDFProcessor()
