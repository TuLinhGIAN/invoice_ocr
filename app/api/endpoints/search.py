from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import datetime
import pandas as pd
import os
from app.schemas.invoice import Invoice, InvoiceSearchRequest
from app.services.database_service import DatabaseService
from app.api.dependencies import get_database_service

router = APIRouter()

@router.get("/summary")
async def get_daily_summary(
    start_date: Optional[datetime] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)"),
    end_date: Optional[datetime] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    ## 📊 Tổng hợp doanh thu theo ngày + Tự động xuất Excel
    
    **Hiển thị bảng tổng hợp và tự động tạo file Excel:**
    
    ### Kết quả JSON:
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
        "period": "2024-01-20 to 2024-01-25"
    }
    ```
    
    ### Tính năng:
    - 📈 **Tổng hợp theo ngày**: Số lượng hóa đơn, tổng tiền, trung bình
    - 📋 **Bảng thống kê**: Hiển thị dữ liệu dễ đọc
    - 📁 **Auto Excel**: Tự động tạo và lưu file Excel
    - 💾 **Download link**: Đường dẫn tải file Excel
    """
    try:
        # Get invoices
        if start_date or end_date:
            invoices = db_service.get_invoices_by_date_range(start_date, end_date)
        else:
            invoices = db_service.get_all_invoices()
        
        if not invoices:
            raise HTTPException(status_code=404, detail="No invoices found")
        
        # Create daily summary
        daily_summary = {}
        for invoice in invoices:
            if invoice.payment_date:
                date_key = invoice.payment_date.strftime('%Y-%m-%d')
                if date_key not in daily_summary:
                    daily_summary[date_key] = {
                        'date': date_key,
                        'invoice_count': 0,
                        'total_amount': 0.0,
                        'invoices': []
                    }
                daily_summary[date_key]['invoice_count'] += 1
                daily_summary[date_key]['total_amount'] += float(invoice.total_amount or 0)
                daily_summary[date_key]['invoices'].append(invoice)
        
        # Calculate averages
        summary_table = []
        for date_data in daily_summary.values():
            summary_table.append({
                'date': date_data['date'],
                'invoice_count': date_data['invoice_count'],
                'total_amount': round(date_data['total_amount'], 2),
                'avg_amount': round(date_data['total_amount'] / date_data['invoice_count'], 2)
            })
        
        # Sort by date
        summary_table.sort(key=lambda x: x['date'])
        
        # Calculate totals
        total_revenue = sum(item['total_amount'] for item in summary_table)
        total_invoices = sum(item['invoice_count'] for item in summary_table)
        
        # Create Excel file with multiple sheets
        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"summary_{timestamp}.xlsx"
        filepath = os.path.join(export_dir, filename)
        
        # Create Excel with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Summary sheet
            summary_df = pd.DataFrame(summary_table)
            summary_df.to_excel(writer, sheet_name='Daily Summary', index=False)
            
            # Detailed invoices sheet
            detailed_data = []
            for invoice in invoices:
                for item in invoice.items:
                    detailed_data.append({
                        'Date': invoice.payment_date.strftime('%Y-%m-%d') if invoice.payment_date else '',
                        'Invoice Code': invoice.invoice_code,
                        'Item Name': item.item_name,
                        'Quantity': item.quantity,
                        'Unit Price': float(item.unit_price) if item.unit_price else 0,
                        'Total Price': float(item.total_price) if item.total_price else 0,
                        'Invoice Total': float(invoice.total_amount) if invoice.total_amount else 0,
                        'Created At': invoice.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            detailed_df = pd.DataFrame(detailed_data)
            detailed_df.to_excel(writer, sheet_name='Detailed Invoices', index=False)
        
        # Determine period
        period = "All time"
        if start_date and end_date:
            period = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        elif start_date:
            period = f"From {start_date.strftime('%Y-%m-%d')}"
        elif end_date:
            period = f"Until {end_date.strftime('%Y-%m-%d')}"
        
        return {
            "summary_table": summary_table,
            "total_revenue": round(total_revenue, 2),
            "total_invoices": total_invoices,
            "excel_file": f"/exports/{filename}",
            "period": period,
            "message": f"✅ Tạo báo cáo thành công! File Excel: {filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary failed: {str(e)}")

@router.get("/{invoice_id}", response_model=Invoice)
async def get_invoice(
    invoice_id: int,
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Get specific invoice by ID
    """
    invoice = db_service.get_invoice(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice