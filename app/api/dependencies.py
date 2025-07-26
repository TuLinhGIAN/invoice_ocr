from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.ocr_service import OCRService
from app.services.extraction_service import ExtractionService
from app.services.database_service import DatabaseService

def get_ocr_service() -> OCRService:
    return OCRService()

def get_extraction_service() -> ExtractionService:
    return ExtractionService()

def get_database_service(db: Session = Depends(get_db)) -> DatabaseService:
    return DatabaseService(db)