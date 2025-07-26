# Vietnamese Invoice OCR System

A complete system for Vietnamese invoice OCR processing with FastAPI backend and Streamlit frontend.

## Features

- **OCR Processing**: Extract text from Vietnamese invoices using Tesseract
- **Key-Value Extraction**: Automatically extract invoice code, payment date, items, and total amount
- **Database Storage**: Store processed invoices in PostgreSQL
- **Search Functionality**: Search invoices by date range
- **Excel Export**: Export search results to Excel files
- **Web Interface**: User-friendly Streamlit interface
- **Docker Support**: Complete containerization with Docker Compose

## Project Structure

```
invoice_ocr/
├── app/                        # FastAPI application
│   ├── api/endpoints/         # API endpoints
│   ├── core/                  # Core configuration
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic services
│   └── utils/                 # Utility functions
├── frontend/                  # Streamlit frontend
├── database/                  # Database scripts
├── docker/                    # Docker configuration
└── tests/                     # Test files
```

## Quick Start with Docker

1. **Clone the repository and navigate to project directory**

2. **Start the application with Docker Compose:**
```bash
cd docker
docker-compose up --build
```

3. **Access the applications:**
   - API: http://localhost:8000
   - Frontend: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## Manual Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- Tesseract OCR with Vietnamese language support

### Installation

1. **Install Tesseract OCR:**

On Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

On macOS:
```bash
brew install tesseract tesseract-lang
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Setup PostgreSQL database:**
```bash
# Create database
createdb invoice_ocr

# Run initialization script
psql -d invoice_ocr -f database/init.sql
```

4. **Configure environment variables:**
```bash
cp .env .env
# Edit .env with your database configuration
```

### Running the Application

1. **Start the FastAPI server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start the Streamlit frontend:**
```bash
streamlit run frontend/app.py --server.port 8501
```

## API Endpoints

### OCR Processing
- `POST /api/ocr/process` - Upload and process invoice image
- `GET /api/ocr/test` - Test OCR service status

### Invoice Search
- `GET /api/invoices/` - Search invoices by date range
- `GET /api/invoices/{id}` - Get specific invoice by ID
- `GET /api/invoices/export` - Export invoices to Excel

## Usage

### Upload Invoice
1. Go to the Streamlit interface
2. Select "Upload Invoice" page
3. Upload an invoice image (JPG, PNG, TIFF, BMP)
4. Click "Process Invoice"
5. View extracted information

### Search Invoices
1. Select "Search Invoices" page
2. Optionally set date range
3. Click "Search Invoices"
4. Export results to Excel if needed

## Development

### Running Tests
```bash
pytest tests/
```

### Code Structure

- **OCR Service** (`app/services/ocr_service.py`): Handles image preprocessing and OCR
- **Extraction Service** (`app/services/extraction_service.py`): Extracts structured data from OCR text
- **Database Service** (`app/services/database_service.py`): Handles database operations
- **API Endpoints**: RESTful API for OCR processing and invoice search

## Supported Languages

The system is optimized for Vietnamese invoices but can be extended for other languages by:
1. Installing additional Tesseract language packs
2. Updating extraction patterns in `extraction_service.py`

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Make sure Tesseract is installed and in PATH
2. **Database connection error**: Check PostgreSQL is running and credentials are correct
3. **OCR accuracy issues**: Ensure invoice images are clear and well-lit

### Configuration

Environment variables can be set in `.env` file:
- `DATABASE_URL`: PostgreSQL connection string
- `TESSERACT_CMD`: Path to tesseract executable
- `UPLOAD_DIR`: Directory for uploaded files
- `MAX_FILE_SIZE`: Maximum file upload size

## License

This project is for educational purposes.