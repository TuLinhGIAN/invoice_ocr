from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    image_data = Column(LargeBinary, nullable=False)
    file_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationship with invoices
    invoices = relationship("Invoice", back_populates="image")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_code = Column(String(100), index=True)
    payment_date = Column(DateTime)
    total_amount = Column(Numeric(12, 2))
    created_at = Column(DateTime, server_default=func.now())
    image_id = Column(Integer, ForeignKey("images.id"))
    raw_text = Column(Text)
    
    # Relationships
    image = relationship("Image", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    item_name = Column(String(255))
    quantity = Column(Integer)
    unit_price = Column(Numeric(10, 2))
    total_price = Column(Numeric(10, 2))
    
    # Relationship back to invoice
    invoice = relationship("Invoice", back_populates="items")