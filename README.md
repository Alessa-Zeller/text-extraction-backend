# PDF Processing API - Production Ready MVP

A robust, production-ready FastAPI application for processing PDF documents with batch processing capabilities, built with security, scalability, and deployment in mind.

## 🚀 Features

### Core Functionality
- **PDF Text Extraction**: Extract text from PDF documents using `pdfplumber`
- **Batch Processing**: Process multiple PDFs concurrently with configurable limits
- **Table Extraction**: Extract and structure table data from PDFs
- **Text Search**: Search for specific text within processed PDF results
- **File Validation**: Comprehensive file type and size validation

### Production Features
- **JWT Authentication**: Secure user authentication and authorization
- **Rate Limiting**: Configurable request rate limiting
- **Error Handling**: Comprehensive error handling with detailed responses
- **Request Validation**: Robust input validation using Pydantic
- **API Versioning**: Structured API versioning (/api/v1/)
- **Environment Configuration**: Flexible configuration management
- **Security Headers**: Security best practices implemented
- **Health Checks**: Service health monitoring endpoints

### Deployment & Operations
- **Docker Support**: Complete containerization with multi-service setup
- **Database Integration**: PostgreSQL with initialization scripts
- **Caching**: Redis integration for performance optimization
- **Reverse Proxy**: Nginx configuration for production deployment
- **Monitoring**: Health checks and service statistics
- **Testing**: Comprehensive test suite with pytest

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- PostgreSQL (for database features)
- Redis (for caching and task queuing)

## 🛠️ Quick Start

### Option 1: Docker Deployment (Recommended for Production)

1. **Clone and navigate to the project:**
   ```bash
   cd /Users/dev/Documents/test_assessment
   ```

2. **Deploy with Docker Compose:**
   ```bash
   ./scripts/deploy.sh
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Option 2: Local Development

1. **Start the development server:**
   ```bash
   ./scripts/start.sh
   ```

2. **Run tests:**
   ```bash
   ./scripts/test.sh
   ```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Get Profile
```http
GET /api/v1/auth/profile
Authorization: Bearer <your-jwt-token>
```

### PDF Processing Endpoints

#### Upload Single PDF
```http
POST /api/v1/pdf/upload
Authorization: Bearer <your-jwt-token>
Content-Type: multipart/form-data

file: <pdf-file>
```

#### Batch Upload PDFs
```http
POST /api/v1/pdf/batch-upload
Authorization: Bearer <your-jwt-token>
Content-Type: multipart/form-data

files: <pdf-file-1>
files: <pdf-file-2>
...
```

#### Search Text in Results
```http
POST /api/v1/pdf/search
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "query": "search term",
  "pdf_results": {<pdf-processing-result>}
}
```

#### Generate PDF Summary
```http
POST /api/v1/pdf/summary
Authorization: Bearer <your-jwt-token>
Content-Type: application/json

{
  "pdf_results": {<pdf-processing-result>}
}
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Project Configuration
PROJECT_NAME="PDF Processing API"
DEBUG=false
ENVIRONMENT=production

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/pdf_processing

# File Processing
MAX_FILE_SIZE=10485760  # 10MB
BATCH_SIZE=10
MAX_CONCURRENT_TASKS=5

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Docker Configuration

The application includes a complete Docker setup:

- **API Service**: FastAPI application
- **Database**: PostgreSQL with initialization
- **Cache**: Redis for performance
- **Proxy**: Nginx for production (optional)

## 🏗️ Architecture

### Project Structure
```
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core functionality (config, security, exceptions)
│   ├── middleware/      # Custom middleware (rate limiting)
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
├── tests/               # Test suite
├── scripts/             # Deployment and utility scripts
├── docker-compose.yml   # Multi-service deployment
├── Dockerfile          # Application container
└── requirements.txt    # Python dependencies
```

### Key Design Decisions

1. **Separation of Concerns**: Clear separation between API, business logic, and data layers
2. **Security First**: JWT authentication, rate limiting, input validation
3. **Error Handling**: Comprehensive exception handling with meaningful responses
4. **Scalability**: Asynchronous processing, batch operations, configurable limits
5. **Production Ready**: Docker deployment, health checks, monitoring

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: BCrypt for password security
- **Rate Limiting**: Configurable request throttling
- **Input Validation**: Comprehensive request validation
- **Security Headers**: CORS, XSS protection, content type validation
- **File Validation**: Type and size restrictions for uploads

## 📊 Monitoring & Health Checks

### Health Endpoints
- `GET /health` - General application health
- `GET /api/v1/pdf/health` - PDF service health

### Rate Limiting Headers
- `X-RateLimit-Limit` - Request limit
- `X-RateLimit-Remaining` - Remaining requests
- `X-RateLimit-Reset` - Reset timestamp

## 🧪 Testing

Run the complete test suite:

```bash
./scripts/test.sh
```

Or run specific tests:

```bash
# Authentication tests
pytest tests/test_auth.py -v

# PDF processing tests
pytest tests/test_pdf.py -v
```

## 🚀 Deployment

### Production Deployment

1. **Configure environment variables** in `.env`
2. **Deploy with Docker Compose:**
   ```bash
   docker-compose up -d
   ```
3. **Verify deployment:**
   ```bash
   curl http://localhost:8000/health
   ```

### Scaling Considerations

- **Horizontal Scaling**: Multiple API instances behind load balancer
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session storage and caching
- **File Storage**: Consider cloud storage for production files
- **Monitoring**: Add APM tools (e.g., New Relic, DataDog)

## 🤝 Default Users

The application comes with default users for testing:

- **Admin User**: `admin@example.com` / `admin123`
- **Regular User**: `user@example.com` / `user123`

## 📝 API Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {<response-data>},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

Error responses:

```json
{
  "error": "Error Type",
  "message": "Detailed error message",
  "details": {<additional-details>},
  "type": "error_type_identifier",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 🔄 Future Enhancements

Potential features for future iterations:

- **Database Integration**: Full ORM with SQLAlchemy
- **Async Task Queue**: Celery for background processing
- **File Storage**: Cloud storage integration (AWS S3, Google Cloud)
- **Advanced Analytics**: Processing statistics and reporting
- **WebSocket Support**: Real-time processing updates
- **Multi-tenancy**: Organization-based access control
- **Advanced Search**: Full-text search with Elasticsearch
- **API Rate Plans**: Tiered access levels

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8000, 5432, 6379 are available
2. **Docker permissions**: Run with appropriate Docker permissions
3. **File upload limits**: Check `MAX_FILE_SIZE` configuration
4. **Memory usage**: Monitor memory for large PDF processing

### Logs

View application logs:
```bash
docker-compose logs -f api
```

## 📄 License

This project is part of a technical assessment and is provided as-is for evaluation purposes.

---

**Built with FastAPI, Python 3.11, and production-ready practices** 🚀
