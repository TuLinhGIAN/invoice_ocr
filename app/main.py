from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.models.invoice import Base
from app.api.endpoints import ocr, search, image

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## Vietnamese Invoice OCR API
    
    Hệ thống OCR hóa đơn tiếng Việt với các tính năng:
    
    ### 📄 OCR Processing
    * Upload và xử lý hình ảnh hóa đơn tiếng Việt
    * Trích xuất tự động: mã hóa đơn, ngày thanh toán, danh sách hàng hóa, tổng tiền
    * Lưu trữ vào database PostgreSQL
    
    ### 🔍 Search & Export
    * Tìm kiếm hóa đơn theo khoảng thời gian
    * Tự động xuất file Excel với tổng hợp dữ liệu
    * Hiển thị thống kê tổng giá trị theo ngày
    
    ### 🛠️ Technical Features
    * Marker OCR với Vietnamese language pack
    * Key-value extraction patterns
    * RESTful API với FastAPI
    * Swagger UI documentation
    """,
    version="1.0.0",
    contact={
        "name": "Vietnamese Invoice OCR",
        "email": "support@invoiceocr.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    ocr.router, 
    prefix=f"{settings.API_V1_STR}",
    tags=["📸 OCR Processing"],
    responses={404: {"description": "Not found"}}
)
app.include_router(
    search.router, 
    prefix=f"{settings.API_V1_STR}",
    tags=["📊 Invoice Management"],
    responses={404: {"description": "Not found"}}
)
app.include_router(
    image.router, 
    prefix=f"{settings.API_V1_STR}/images", 
    tags=["🖼️ Image Management"],
    responses={404: {"description": "Not found"}}
)

@app.get("/")
async def root():
    return {"message": "Vietnamese Invoice OCR API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}