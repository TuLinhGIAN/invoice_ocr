from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class InvoiceItemBase(BaseModel):
    item_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

class InvoiceItemCreate(InvoiceItemBase):
    pass

class InvoiceItem(InvoiceItemBase):
    id: int
    invoice_id: int
    
    class Config:
        from_attributes = True

class InvoiceBase(BaseModel):
    invoice_code: Optional[str] = None
    payment_date: Optional[datetime] = None
    total_amount: Optional[Decimal] = None

class InvoiceCreate(InvoiceBase):
    image_id: int
    raw_text: str
    items: List[InvoiceItemCreate] = []

class Invoice(InvoiceBase):
    id: int
    created_at: datetime
    image_id: Optional[int] = None
    raw_text: str
    items: List[InvoiceItem] = []
    
    class Config:
        from_attributes = True

class InvoiceSearchRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class OCRResponse(BaseModel):
    invoice_code: Optional[str]
    payment_date: Optional[datetime]
    total_amount: Optional[Decimal]
    items: List[InvoiceItemCreate]
    raw_text: str