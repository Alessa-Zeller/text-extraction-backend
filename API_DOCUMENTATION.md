# PDF Processing API - Detailed Documentation

## 📖 Table of Contents
- [Authentication](#authentication)
- [PDF Processing](#pdf-processing)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Data Models](#data-models)
- [Examples](#examples)

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid Bearer token.

### Authentication Flow

1. **Register** or **Login** to get tokens
2. **Include** the access token in the Authorization header
3. **Refresh** tokens when they expire

### Endpoints

#### POST `/api/v1/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST `/api/v1/auth/login`

Authenticate an existing user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as registration response.

#### POST `/api/v1/auth/refresh`

Refresh an access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### GET `/api/v1/auth/profile`

Get current user profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "user_id": "user_123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_admin": false,
    "created_at": "2024-01-01T00:00:00Z"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST `/api/v1/auth/logout`

Logout the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

## 📄 PDF Processing

### Core Features

- Extract text from PDF documents
- Process multiple files in batches
- Extract tables from PDFs
- Search within extracted content
- Generate processing summaries

### Endpoints

#### POST `/api/v1/pdf/upload`

Upload and process a single PDF file.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
file: <PDF file>
```

**Response:**
```json
{
  "success": true,
  "message": "PDF processed successfully",
  "data": {
    "filename": "document.pdf",
    "file_size": 1024000,
    "processed_at": "2024-01-01T12:00:00Z",
    "pages": [
      {
        "page_number": 1,
        "text": "Extracted text content...",
        "text_length": 500,
        "tables": [],
        "bbox": [0, 0, 612, 792],
        "width": 612,
        "height": 792
      }
    ],
    "total_pages": 1,
    "total_text_length": 500,
    "metadata": {
      "title": "Document Title",
      "author": "Document Author"
    },
    "file_hash": "a1b2c3d4e5f6...",
    "status": "success",
    "processed_by": "user_123"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST `/api/v1/pdf/batch-upload`

Upload and process multiple PDF files in batch.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
files: <PDF file 1>
files: <PDF file 2>
files: <PDF file 3>
...
```

**Constraints:**
- Maximum 10 files per batch (configurable)
- Each file must be a PDF
- Each file must be under the size limit (10MB default)

**Response:**
```json
{
  "success": true,
  "message": "Batch processing completed. 3 files processed successfully, 0 failed.",
  "data": {
    "batch_id": "batch_abc123",
    "processed_at": "2024-01-01T12:00:00Z",
    "total_files": 3,
    "successful": [
      {<pdf_processing_result_1>},
      {<pdf_processing_result_2>},
      {<pdf_processing_result_3>}
    ],
    "failed": [],
    "summary": {
      "success_count": 3,
      "error_count": 0,
      "total_pages": 15,
      "total_text_length": 5000
    },
    "processed_by": "user_123"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST `/api/v1/pdf/search`

Search for text within PDF processing results.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "search term",
  "pdf_results": {<pdf_processing_result>}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Search completed. Found 3 matches.",
  "data": {
    "query": "search term",
    "matches": [
      {
        "page_number": 1,
        "matches": [
          {
            "position": 150,
            "context": "...text before search term text after...",
            "match_text": "search term"
          }
        ],
        "match_count": 1
      }
    ],
    "total_matches": 3,
    "pages_with_matches": 2
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST `/api/v1/pdf/summary`

Generate a summary of PDF processing results.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "pdf_results": {<pdf_processing_result>}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Summary generated successfully",
  "data": {
    "filename": "document.pdf",
    "total_pages": 10,
    "total_text_length": 5000,
    "average_page_length": 500,
    "longest_page": 800,
    "shortest_page": 200,
    "pages_with_tables": 3,
    "total_tables": 5,
    "file_size": 1024000,
    "processed_at": "2024-01-01T12:00:00Z",
    "metadata": {<pdf_metadata>}
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Health and Statistics

#### GET `/api/v1/pdf/health`

Check PDF service health.

**Response:**
```json
{
  "success": true,
  "message": "PDF service is healthy",
  "data": {
    "service": "pdf_processor",
    "status": "healthy",
    "max_batch_size": 10,
    "max_file_size": 10485760,
    "allowed_file_types": [".pdf"]
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET `/api/v1/pdf/stats` (Admin Only)

Get processing statistics.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Processing statistics retrieved successfully",
  "data": {
    "total_files_processed": 1500,
    "total_pages_processed": 15000,
    "total_text_extracted": 5000000,
    "average_processing_time": 2500,
    "success_rate": 98.5,
    "most_common_errors": [
      {"error": "corrupted_pdf", "count": 15},
      {"error": "file_too_large", "count": 8}
    ],
    "service_uptime": "15 days, 4 hours"
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## ❌ Error Handling

The API provides comprehensive error handling with detailed error responses.

### Error Response Format

```json
{
  "error": "Error Type",
  "message": "Human-readable error description",
  "details": "Additional error details or null",
  "type": "error_type_identifier",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Common Error Types

#### Authentication Errors (401)
```json
{
  "error": "Authentication Error",
  "message": "Could not validate credentials",
  "type": "authentication_error",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Authorization Errors (403)
```json
{
  "error": "Authorization Error", 
  "message": "Not enough permissions",
  "type": "authorization_error",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Validation Errors (422)
```json
{
  "error": "Validation Error",
  "message": "Request validation failed",
  "details": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ],
  "type": "validation_error",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### File Validation Errors (400)
```json
{
  "error": "File Validation Error",
  "message": "File size exceeds maximum allowed size",
  "filename": "large_document.pdf",
  "type": "file_validation_error",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### PDF Processing Errors (422)
```json
{
  "error": "PDF Processing Error",
  "message": "Failed to extract text from PDF",
  "details": "File appears to be corrupted",
  "type": "pdf_processing_error",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

#### Batch Processing Errors (422)
```json
{
  "error": "Batch Processing Error",
  "message": "Some files in the batch failed to process",
  "failed_items": ["file1.pdf", "file3.pdf"],
  "type": "batch_processing_error",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## 🚦 Rate Limiting

The API implements rate limiting to ensure fair usage and system stability.

### Rate Limit Headers

Every response includes rate limiting information:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704110400
```

### Rate Limit Exceeded (429)

When rate limits are exceeded:

```json
{
  "error": "Rate Limit Exceeded",
  "message": "Too many requests. Limit: 100 requests per 60 seconds",
  "retry_after": 45,
  "type": "rate_limit_error"
}
```

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704110400
Retry-After: 45
```

### Default Limits

- **Requests**: 100 per 60 seconds per IP
- **Burst**: Up to 20 requests can burst above the limit
- **Excluded Endpoints**: `/health`, `/docs`, `/redoc`, `/openapi.json`

## 📊 Data Models

### User Profile
```json
{
  "user_id": "string",
  "email": "string",
  "full_name": "string|null",
  "is_admin": "boolean",
  "created_at": "string|null",
  "last_login": "string|null"
}
```

### PDF Page
```json
{
  "page_number": "integer (≥1)",
  "text": "string",
  "text_length": "integer (≥0)",
  "tables": "array of tables",
  "bbox": "array of floats|null",
  "width": "float (≥0)|null",
  "height": "float (≥0)|null",
  "error": "string|null"
}
```

### PDF Processing Result
```json
{
  "filename": "string",
  "file_size": "integer (≥0)",
  "processed_at": "string (ISO datetime)",
  "pages": "array of PDFPage",
  "total_pages": "integer (≥0)",
  "total_text_length": "integer (≥0)",
  "metadata": "object",
  "file_hash": "string",
  "status": "string"
}
```

### Search Result
```json
{
  "query": "string",
  "matches": "array of page matches",
  "total_matches": "integer (≥0)",
  "pages_with_matches": "integer (≥0)"
}
```

## 💡 Examples

### Complete Workflow Example

1. **Register a user:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

2. **Upload a PDF:**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@document.pdf"
```

3. **Search in results:**
```bash
curl -X POST "http://localhost:8000/api/v1/pdf/search" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "important information",
    "pdf_results": {PDF_PROCESSING_RESULT}
  }'
```

### Batch Processing Example

```bash
curl -X POST "http://localhost:8000/api/v1/pdf/batch-upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf" \
  -F "files=@document3.pdf"
```

### Error Handling Example

```javascript
async function uploadPDF(file, token) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('/api/v1/pdf/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const result = await response.json();
    
    if (!response.ok) {
      throw new Error(result.message || 'Upload failed');
    }
    
    return result.data;
  } catch (error) {
    console.error('Upload error:', error.message);
    throw error;
  }
}
```

---

For more information, visit the interactive API documentation at `/docs` when the server is running.
