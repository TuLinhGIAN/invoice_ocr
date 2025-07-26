# 📘 Vietnamese Invoice OCR API - Usage Guide

## 🚀 Quick Start

### Start API Server:
```bash
python run_server.py  
```

### Access Swagger UI:
**🌐 http://localhost:8000/docs**

---

## 📸 OCR Processing Endpoints

### 1. **POST** `/api/ocr/process` - Upload và xử lý hóa đơn

**📋 Description:** Upload hình ảnh hóa đơn và trích xuất thông tin tự động

**📥 Input:** 
- File hình ảnh (JPG, PNG, TIFF, BMP)
- Max size: 10MB

**📤 JSON Response:**
```json
{
  "id": 1,
  "invoice_code": "HD2024001",
  "payment_date": "2024-01-25T00:00:00",
  "total_amount": 130000.00,
  "created_at": "2024-01-25T08:30:00",
  "image_path": "/uploads/invoice.jpg",
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

---

## 📊 Invoice Management Endpoints

### 2. **GET** `/api/invoices/` - Tìm kiếm hóa đơn

**📋 Description:** Truy vấn danh sách hóa đơn theo khoảng thời gian

**⚙️ Parameters:**
- `start_date` (optional): Ngày bắt đầu (YYYY-MM-DD)
- `end_date` (optional): Ngày kết thúc (YYYY-MM-DD)

**📤 Response:** Array of invoices with full details

### 3. **GET** `/api/invoices/summary` - 📊 Tổng hợp + Auto Excel

**🎯 Key Feature:** **Hiển thị bảng tổng hợp theo ngày + Tự động tạo Excel**

**📤 JSON Response:**
```json
{
  "summary_table": [
    {
      "date": "2024-01-25",
      "invoice_count": 5,
      "total_amount": 650000.00,
      "avg_amount": 130000.00
    }
  ],
  "total_revenue": 650000.00,
  "total_invoices": 5,
  "excel_file": "/exports/summary_20240125_143022.xlsx",
  "period": "2024-01-20 to 2024-01-25",
  "message": "✅ Tạo báo cáo thành công!"
}
```

**🔥 Features:**
- 📈 **Daily Summary:** Số lượng + tổng tiền + trung bình theo ngày
- 📁 **Auto Excel:** Tự động tạo file Excel với 2 sheets:
  - **Daily Summary:** Tổng hợp theo ngày  
  - **Detailed Invoices:** Chi tiết từng hóa đơn
- 💾 **File Path:** Trả về đường dẫn file Excel đã tạo

### 4. **GET** `/api/invoices/export` - 📁 Download Excel

**📋 Description:** Download trực tiếp file Excel chi tiết

**📤 Response:** File Excel (.xlsx) - Auto download

### 5. **GET** `/api/invoices/{invoice_id}` - Chi tiết hóa đơn

**📋 Description:** Lấy thông tin chi tiết 1 hóa đơn theo ID

---

## 🧪 Test Endpoints

### 6. **GET** `/api/ocr/test` - Test OCR Service
**📤 Response:** `{"message": "OCR service is running"}`

### 7. **GET** `/health` - Health Check  
**📤 Response:** `{"status": "healthy"}`

---

## 🔧 Technical Features

### ✅ Vietnamese OCR:
- **Tesseract** với Vietnamese language pack (`vie`)
- **Smart extraction** patterns cho tiếng Việt
- **Unicode support** đầy đủ

### ✅ Database:
- **PostgreSQL** with SQLAlchemy ORM
- **Auto-create tables** on startup
- **Relationship mapping** Invoice ↔ Items

### ✅ File Handling:
- **Secure upload** with validation
- **Auto-cleanup** and path management
- **Multi-format support**

### ✅ Excel Export:
- **Pandas + openpyxl** for Excel generation
- **Multi-sheet** workbooks
- **Auto-formatting** and timestamps

---

## 🎯 Swagger UI Features

**🌐 Access:** http://localhost:8000/docs

### Enhanced Documentation:
- 📸 **OCR Processing** section with detailed examples
- 📊 **Invoice Management** section with JSON samples  
- 🔧 **Interactive testing** right in the browser
- 📋 **Response schemas** with real examples
- 🚀 **Try it out** functionality for all endpoints

### Visual Organization:
- **Emoji tags** for easy navigation
- **Rich descriptions** with examples
- **Parameter documentation** in Vietnamese
- **Error handling** examples

---

## 🎉 Ready for Production!

Hệ thống đã sẵn sàng cho bài tập cuối khóa với:
- ✅ **Vietnamese OCR** processing
- ✅ **Database integration** 
- ✅ **Excel export** tự động
- ✅ **Beautiful Swagger UI**
- ✅ **Complete API documentation**

**Start testing:** `python run_server.py` → http://localhost:8000/docs