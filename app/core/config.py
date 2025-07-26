from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/invoice_ocr"
    
    # API settings
    API_V1_STR: str = "/invoice"
    PROJECT_NAME: str = "Invoice OCR API"
    
    # OCR settings
    TESSERACT_CMD: Optional[str] = None  # Path to tesseract executable if needed
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings()