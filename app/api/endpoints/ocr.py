from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response
from app.schemas.invoice import Invoice, OCRResponse
from app.services.ocr_service import OCRService
from app.services.extraction_service import ExtractionService
from app.services.database_service import DatabaseService
from app.api.dependencies import get_ocr_service, get_extraction_service, get_database_service
from app.utils.file_handler import validate_file
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

router = APIRouter()

@router.post("/extract", response_model=Invoice)
async def process_invoice(
    file: UploadFile = File(..., description="Hình ảnh hóa đơn (JPG, PNG, TIFF, BMP)"),
    ocr_service: OCRService = Depends(get_ocr_service),
    extraction_service: ExtractionService = Depends(get_extraction_service),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    ## 📸 Xử lý OCR Hóa đơn tiếng Việt
    
    **Upload hình ảnh hóa đơn và trích xuất thông tin tự động:**
    
    ### Đầu vào:
    - **file**: Hình ảnh hóa đơn (JPG, PNG, TIFF, BMP)
    - **Kích thước tối đa**: 10MB
    
    ### Đầu ra JSON:
    ```json
    {
        "id": 1,
        "invoice_code": "HD2024001",
        "payment_date": "2024-01-25T00:00:00",
        "total_amount": 130000.00,
        "created_at": "2024-01-25T08:30:00",
        "image_id": 1,
        "raw_text": "HÓA ĐƠN BÁN HÀNG...",
        "items": [
            {
                "id": 1,
                "item_name": "Cà phê sữa đá",
                "quantity": 2,
                "unit_price": 30000.00,
                "total_price": 60000.00
            }
        ]
    }
    ```
    
    ### Quá trình xử lý:
    1. ✅ **Validate file**: Kiểm tra định dạng và kích thước
    2. 🔍 **OCR**: Trích xuất text từ hình ảnh bằng Tesseract (Vietnamese)
    3. 📊 **Extract**: Phân tích và trích xuất thông tin có cấu trúc
    4. 💾 **Save**: Lưu vào database PostgreSQL
    """
    try:
        # Validate uploaded file
        validate_file(file)
        
        # Read file content
        file_content = await file.read()
        
        # Process image data
        image_info = ocr_service.process_image_bytes(file_content, file.filename, file.content_type)
        
        # Save image to database FIRST to avoid connection timeout
        print(f"Saving image to database: {file.filename}")
        db_image = db_service.create_image(image_info)
        print(f"Image saved with ID: {db_image.id}")
        
        # Perform OCR with timeout and async processing
        print(f"Starting OCR processing for {file.filename}...")
        start_time = time.time()
        
        try:
            # Run OCR in thread pool with timeout  
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                try:
                    # Set timeout to 300 seconds (5 minutes) for Marker processing
                    raw_text = await asyncio.wait_for(
                        loop.run_in_executor(executor, ocr_service.extract_text, file_content),
                        timeout=300.0
                    )
                    processing_time = time.time() - start_time
                    print(f"OCR completed in {processing_time:.2f} seconds")
                    
                except asyncio.TimeoutError:
                    processing_time = time.time() - start_time
                    print(f"OCR timeout after {processing_time:.2f} seconds")
                    raise HTTPException(status_code=408, detail="OCR processing timeout (300s)")
                except Exception as e:
                    processing_time = time.time() - start_time
                    print(f"OCR failed after {processing_time:.2f} seconds: {str(e)}")
                    raise
        except Exception as e:
            # If OCR fails, we still have the image saved, so return partial result
            print(f"OCR processing failed, but image is saved: {str(e)}")
            raise
        
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="No text found in image")
        
        # Extract structured information
        ocr_response = extraction_service.extract_all(raw_text)
        
        # Save to database
        db_invoice = db_service.create_invoice_from_ocr(ocr_response, db_image.id)
        
        return db_invoice
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
