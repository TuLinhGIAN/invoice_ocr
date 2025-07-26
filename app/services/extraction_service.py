import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from app.schemas.invoice import InvoiceItemCreate, OCRResponse

class ExtractionService:
    def __init__(self):
        # Vietnamese patterns for invoice extraction, optimized for Marker output
        self.patterns = {
            'invoice_code': [
                # Most specific patterns first to avoid picking up lookup codes
                r'ký hiệu\s*\(serial\)\s*:\s*([A-Z0-9\-/]+)(?:\s+s6)?',
                r'serial\s*\)\s*:\s*([A-Z0-9\-/]+)(?:\s+s6)?',
                r'([A-Z0-9]+TDM)(?:\s+s6)?',
                # Avoid matching lookup codes (ANCF8E1SW3 pattern)
                r'(?:ký hiệu|serial)[:\s]*([A-Z0-9\-/]+)(?!\s*$)',
                r'(?:số|number)[:\s]*([A-Z0-9\-/]+)(?!\s*$)',
            ],
            'date': [
                r'ngày\s*(\d{1,2})\s*tháng\s*(\d{1,2})\s*năm\s*(\d{4})',
                r'ngày[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
                r'date[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})'
            ],
            'total_amount': [
                # Specific patterns for Vietnamese invoices
                r'tổng tiền thanh toán\s*[/\(]*[^:]*:\s*([0-9.,]+)',
                r'grand total[)]*:\s*([0-9.,]+)',
                r'tổng\s*(?:cộng|tiền)\s*thanh\s*toán[^:]*:\s*([0-9.,]+)',
                # General patterns
                r'tổng\s*(?:cộng|tiền)[:\s]*([0-9.,]+)',
                r'total[:\s]*([0-9.,]+)',
                # Last resort - specific format pattern
                r'([0-9]{1,3}(?:\.[0-9]{3})*)\s*(?:đồng|vnd)?$',
            ],
            'items': [
                # Table row patterns for Marker markdown
                r'\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|\s*([0-9.,]+)\s*\|\s*([0-9.,]+)\s*\|',
                r'(\d+)\s+([^|]+?)\s+([^|]+?)\s+(\d+)\s+([0-9.,]+)\s+([0-9.,]+)',
                r'(\d+)\s+([^\d\n]+?)\s+(\d+)\s+([0-9.,]+)\s+([0-9.,]+)',
                r'([^\n]+?)\s+(\d+)\s+([0-9.,]+)\s+([0-9.,]+)'
            ]
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Convert to lowercase for pattern matching
        return text.lower().strip()
    
    def extract_invoice_code(self, text: str) -> Optional[str]:
        """Extract invoice code from text"""
        clean_text = self.clean_text(text)
        
        for pattern in self.patterns['invoice_code']:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                # Handle patterns that might not have a capture group
                try:
                    return match.group(1).upper()
                except IndexError:
                    return match.group(0).upper()
        return None
    
    def extract_date(self, text: str) -> Optional[datetime]:
        """Extract payment date from text"""
        clean_text = self.clean_text(text)
        
        # Special handling for Vietnamese date format from Marker
        vn_date_match = re.search(r'ngày\s*(\d{1,2})\s*tháng\s*(\d{1,2})\s*năm\s*(\d{4})', clean_text, re.IGNORECASE)
        if vn_date_match:
            try:
                day, month, year = vn_date_match.groups()
                return datetime(int(year), int(month), int(day))
            except ValueError:
                pass
        
        for pattern in self.patterns['date']:
            match = re.search(pattern, clean_text)
            if match:
                if len(match.groups()) == 3:  # Vietnamese format already handled above
                    continue
                date_str = match.group(1)
                try:
                    # Try different date formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except ValueError:
                    continue
        return None
    
    def extract_total_amount(self, text: str) -> Optional[Decimal]:
        """Extract total amount from text"""
        clean_text = self.clean_text(text)
        
        for pattern in self.patterns['total_amount']:
            match = re.search(pattern, clean_text)
            if match:
                try:
                    amount_str = match.group(1)
                except IndexError:
                    amount_str = match.group(0)
                    
                # Clean amount string
                amount_str = re.sub(r'[,.](?=\d{3})', '', amount_str)  # Remove thousand separators
                amount_str = amount_str.replace(',', '.')  # Convert comma to decimal point
                try:
                    return Decimal(amount_str)
                except:
                    continue
        return None
    
    def extract_items_from_marker_table(self, text: str) -> List[InvoiceItemCreate]:
        """Extract items from Marker structured text output"""
        items = []
        lines = text.split('\n')
        
        # Look for item data that spans multiple lines
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for item number at start of line (1, 2, 3, etc.) or math symbols like \mathfrak{D}
            if (re.match(r'^\d+$', line) or re.match(r'^\\math.*[a-zA-Z].*$', line)) and i + 4 < len(lines):
                # Check if this looks like an item sequence
                item_num = line
                name_line = lines[i + 1].strip()
                
                # Skip if name looks like headers or is too short
                if (any(word in name_line.lower() for word in ['stt', 'description', 'unit', 'quantity', 'price', 'amount', 'tên hàng', 'dvt']) or
                    len(name_line) < 5 or not 'phí' in name_line.lower()):
                    i += 1
                    continue
                
                unit_line = lines[i + 2].strip()
                
                # Initialize variables
                unit_price = None
                total_price = None
                qty = 1
                
                # Try to parse the sequence after name_line
                # Check if we have quantity after unit
                if i + 5 < len(lines):
                    line3 = lines[i + 3].strip()  # Could be quantity
                    line4 = lines[i + 4].strip()  # Could be unit_price
                    line5 = lines[i + 5].strip()  # Could be total_price
                    
                    # Pattern 1: unit, quantity, unit_price, total_price
                    if line3.isdigit() and self._clean_price(line4) and self._clean_price(line5):
                        qty = int(line3)
                        unit_price = self._clean_price(line4)
                        total_price = self._clean_price(line5)
                    
                # Fallback: unit, unit_price, total_price (no quantity)
                if not unit_price and i + 4 < len(lines):
                    line3 = lines[i + 3].strip()
                    line4 = lines[i + 4].strip()
                    
                    unit_price = self._clean_price(line3)
                    total_price = self._clean_price(line4)
                    qty = 1
                
                # Validate and add the item
                if (name_line and len(name_line) >= 5 and 
                    unit_price and total_price and 
                    unit_price > 0 and total_price > 0 and
                    'phí' in name_line.lower()):
                    
                    items.append(InvoiceItemCreate(
                        item_name=name_line,
                        quantity=qty,
                        unit_price=unit_price,
                        total_price=total_price
                    ))
                    
                    # Skip the lines we've processed
                    i += 6 if qty > 1 and i + 5 < len(lines) else 5
                else:
                    i += 1
            else:
                i += 1
        
        return items
    
    def extract_items_fallback(self, text: str) -> List[InvoiceItemCreate]:
        """Fallback method for extracting items using regex patterns"""
        items = []
        
        # Look for specific invoice items in the text
        # Based on the sample: "1 | Phi dịch vụ vệ sinh sofa | | Chiếc | | 450,000 | 450,000"
        item_matches = re.findall(
            r'(\d+)\s*\|\s*([^|]+?)\s*\|\s*[^|]*\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([0-9.,]+)\s*\|\s*([0-9.,]+)',
            text
        )
        
        for match in item_matches:
            try:
                stt, name, unit, empty, unit_price_str, total_str = match
                
                # Clean the name
                name = re.sub(r'<[^>]+>', '', name).strip()
                if len(name) < 3 or 'phi' not in name.lower():
                    continue
                
                # Get quantities and prices
                qty = 1  # Default quantity
                unit_price = self._clean_price(unit_price_str)
                total_price = self._clean_price(total_str)
                
                if unit_price and total_price:
                    items.append(InvoiceItemCreate(
                        item_name=name,
                        quantity=qty,
                        unit_price=unit_price,
                        total_price=total_price
                    ))
            except (ValueError, IndexError):
                continue
        
        return items
    
    def extract_items(self, text: str) -> List[InvoiceItemCreate]:
        """Extract line items from text - enhanced for Marker output"""
        # First try to extract from Marker table format
        items = self.extract_items_from_marker_table(text)
        
        # If no items found, try fallback method
        if not items:
            items = self.extract_items_fallback(text)
        
        return items
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text"""
        if not text or text.strip() == '':
            return 1  # Default quantity
        
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return None
    
    def _clean_price(self, price_str: str) -> Optional[Decimal]:
        """Clean and convert price string to Decimal"""
        try:
            # Remove non-numeric characters except dots and commas
            clean_price = re.sub(r'[^\d.,]', '', price_str)
            # Handle thousand separators
            clean_price = re.sub(r'[,.](?=\d{3})', '', clean_price)
            clean_price = clean_price.replace(',', '.')
            return Decimal(clean_price) if clean_price else None
        except:
            return None
    
    def extract_all(self, text: str) -> OCRResponse:
        """Extract all information from OCR text"""
        print(f"🔍 Starting extraction from text (length: {len(text)})")
        print(f"📝 First 300 chars: {text[:300]}")
        
        invoice_code = self.extract_invoice_code(text)
        print(f"📋 Invoice code: {invoice_code}")
        
        payment_date = self.extract_date(text)
        print(f"📅 Payment date: {payment_date}")
        
        total_amount = self.extract_total_amount(text)
        print(f"💰 Total amount: {total_amount}")
        
        items = self.extract_items(text)
        print(f"📦 Items found: {len(items)}")
        for i, item in enumerate(items):
            print(f"  Item {i+1}: {item.item_name} - {item.quantity} x {item.unit_price} = {item.total_price}")
        
        return OCRResponse(
            invoice_code=invoice_code,
            payment_date=payment_date,
            total_amount=total_amount,
            items=items,
            raw_text=text
        )