# Sample PDFs for Testing

This directory contains sample PDF files for testing the PDF Processing API.

## Usage

1. **Single Upload Test:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/pdf/upload" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@sample_pdfs/sample_document.pdf"
   ```

2. **Batch Upload Test:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/pdf/batch-upload" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "files=@sample_pdfs/sample_document.pdf" \
     -F "files=@sample_pdfs/sample_table.pdf"
   ```

## Sample Files

- **sample_document.pdf**: Basic text document for testing text extraction
- **sample_table.pdf**: Document with tables for testing table extraction
- **sample_large.pdf**: Larger document for testing batch processing

Note: Add your own PDF files to this directory for testing. The API supports PDF files up to 10MB by default.
