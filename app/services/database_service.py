from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.invoice import Invoice, InvoiceItem, Image
from app.schemas.invoice import InvoiceCreate, OCRResponse

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_image(self, image_info: dict) -> Image:
        """Create image record in database"""
        try:
            db_image = Image(
                filename=image_info["filename"],
                content_type=image_info["content_type"],
                image_data=image_info["image_data"],
                file_size=image_info["file_size"]
            )
            
            self.db.add(db_image)
            self.db.commit()
            self.db.refresh(db_image)
            return db_image
        except Exception as e:
            self.db.rollback()
            print(f"Database error creating image: {str(e)}")
            raise
    
    def create_invoice_from_ocr(self, ocr_response: OCRResponse, image_id: int) -> Invoice:
        """Create invoice from OCR response"""
        try:
            # Create invoice
            db_invoice = Invoice(
                invoice_code=ocr_response.invoice_code,
                payment_date=ocr_response.payment_date,
                total_amount=ocr_response.total_amount,
                image_id=image_id,
                raw_text=ocr_response.raw_text
            )
            
            self.db.add(db_invoice)
            self.db.flush()  # Get the ID
            
            # Create invoice items
            for item in ocr_response.items:
                db_item = InvoiceItem(
                    invoice_id=db_invoice.id,
                    item_name=item.item_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
                self.db.add(db_item)
            
            self.db.commit()
            self.db.refresh(db_invoice)
            return db_invoice
        except Exception as e:
            self.db.rollback()
            print(f"Database error creating invoice: {str(e)}")
            raise
    
    def get_invoice(self, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    def get_invoices_by_date_range(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> List[Invoice]:
        """Get invoices within date range"""
        query = self.db.query(Invoice)
        
        if start_date:
            query = query.filter(Invoice.payment_date >= start_date)
        if end_date:
            query = query.filter(Invoice.payment_date <= end_date)
        
        return query.order_by(Invoice.payment_date.desc()).all()
    
    def get_all_invoices(self) -> List[Invoice]:
        """Get all invoices"""
        return self.db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    
    def get_image(self, image_id: int) -> Optional[Image]:
        """Get image by ID"""
        return self.db.query(Image).filter(Image.id == image_id).first()
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """Delete invoice by ID"""
        invoice = self.get_invoice(invoice_id)
        if invoice:
            self.db.delete(invoice)
            self.db.commit()
            return True
        return False