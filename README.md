# Vietnamese Invoice OCR System

A complete system for Vietnamese invoice OCR processing with FastAPI backend.
This project is for educational purpose only.

## Features

- **OCR Processing**: Extract text from Vietnamese invoices using Marker OCR
- **Key-Value Extraction**: Automatically extract invoice code, payment date, items, and total amount
- **Database Storage**: Store processed invoices in PostgreSQL
- **Search Functionality**: Search invoices by date range
- **Excel Export**: Export search results to Excel files
- **Docker Support**: Complete containerization with Docker Compose

## Project Structure

```
invoice_ocr/
├── app/                       # FastAPI application
│   ├── api/endpoints/         # API endpoints
│   ├── core/                  # Core configuration
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/              # Business logic services
│   └── utils/                 # Utility functions
├── database/                  # Database scripts
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
   - API Documentation: http://localhost:8000/docs

## Manual Setup

### Prerequisites

- Python 3.9+
- PostgreSQL
- Marker OCR with Vietnamese language support

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup PostgreSQL database:**
```bash
# Create database
createdb invoice_ocr

# Run initialization script
psql -d invoice_ocr -f database/init.sql
```

3. **Configure environment variables:**
```bash
cp .env .env
# Edit .env with your database configuration
```

### Running the Application

**Start the FastAPI server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### OCR Processing
- `POST /invoice/extract` - Upload and process invoice image

### Invoice Search
- `GET /invoice/summary` - Get specific invoice by ID
- `GET /invoice/image` - Export invoices to Excel

## Usage

### Upload Invoice
1. Go to the FastAPI swagger
2. Select "Upload Invoice" page
3. Upload an sample invoice image attached in folder sample
4. Click "Process Invoice"
5. View extracted information

### Search Invoices
1. Select "Search Invoices" page
2. Optionally set date range
3. Click "Search Invoices"
4. Export results to Excel if needed

### Code Structure

- **OCR Service** (`app/services/ocr_service.py`): Handles image preprocessing and OCR
- **Extraction Service** (`app/services/extraction_service.py`): Extracts structured data from OCR text
- **Database Service** (`app/services/database_service.py`): Handles database operations
- **API Endpoints**: RESTful API for OCR processing and invoice search

## Troubleshooting

## License

This project is for educational purposes.