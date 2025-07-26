import cv2
import numpy as np
from PIL import Image
import io
import tempfile
import os
import re
from marker.converters.pdf import PdfConverter
from marker.config.parser import ConfigParser
from marker.models import create_model_dict


class OCRService:
    def __init__(self):
        # Configuration for Vietnamese invoice processing
        self.config = {
            # Enable LLM for better accuracy
            "use_llm": False,

            # OCR and formatting options
            "force_ocr": True,  # Force OCR on entire document
            "format_lines": True,  # Reformat lines for better quality
            "redo_inline_math": False,  # High quality inline math conversion

            # Output format
            "output_format": "json",  # JSON format to easily extract tables

            # Performance settings
            "paginate_output": False,
            "disable_image_extraction": True,
        }
        
        # Models are pre-loaded during startup, so we can initialize immediately
        print("🔄 Initializing OCR Service with pre-loaded models...")
        self.model_dict = create_model_dict()
        
        config_parser = ConfigParser(self.config)
        
        # Initialize PdfConverter with pre-loaded models
        self.converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=self.model_dict,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
        )
        print("✅ OCR Service initialized with pre-loaded models")
    
    def _extract_text_from_json_output(self, document) -> str:
        """Extract text content from Marker JSONOutput structure"""
        text_content = []
        
        def extract_from_block(block):
            """Recursively extract text from JSONBlockOutput"""
            # Process children recursively
            if hasattr(block, 'children') and block.children:
                for child in block.children:
                    extract_from_block(child)
            elif hasattr(block, 'html') and block.html:
                # Clean HTML and extract text
                html_text = block.html
                # Remove HTML tags and get clean text
                clean_text = re.sub(r'<[^>]+>', ' ', html_text)
                # Clean up whitespace and special characters
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                if clean_text:
                    text_content.append(clean_text)
        # Extract from document and all children
        extract_from_block(document)
        
        # Join all text content with newlines
        full_text = '\n'.join(text_content)
        return full_text
        
    def _image_to_pdf(self, image_data: bytes) -> str:
        """Convert image to temporary PDF file for Marker processing"""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            # Save image as PDF with high quality for better OCR
            image.save(temp_pdf.name, format='PDF', quality=95, optimize=True)
            return temp_pdf.name
    
    def extract_text(self, image_data: bytes) -> str:
        """Extract text from image using Marker with optimizations"""
        temp_pdf_path = None
        try:
            print("Starting Marker OCR processing...")
            
            # Convert image to temporary PDF
            temp_pdf_path = self._image_to_pdf(image_data)
            print(f"Created temporary PDF: {temp_pdf_path}")
            
            # Process with Marker - optimized for speed
            print("Processing PDF with Marker...")

            # Convert PDF using PdfConverter
            document = self.converter(temp_pdf_path)
            print(f"Document type: {type(document)}")
            
            # Extract text from Marker JSONOutput
            if hasattr(document, 'children') and document.children:
                # This is a JSONOutput object, extract HTML content from table cells
                full_text = self._extract_text_from_json_output(document)
                print(f"Extracted clean text: {full_text[:500]}...")  # Debug: show first 500 chars
            elif hasattr(document, 'markdown'):
                # Fallback to markdown if available
                full_text = document.markdown
                print(f"Using markdown: {full_text[:500]}...")
            else:
                # Last resort - convert to string
                full_text = str(document)
                print(f"Using string conversion: {full_text[:500]}...")

            print(f"Extracted {len(full_text)} characters")

            return full_text if full_text.strip() else "No text detected"
            
        except Exception as e:
            print(f"Marker OCR error: {str(e)}")
            raise Exception(f"Marker OCR failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_pdf_path and os.path.exists(temp_pdf_path):
                try:
                    os.unlink(temp_pdf_path)
                    print(f"Cleaned up temporary file: {temp_pdf_path}")
                except:
                    pass  # Ignore cleanup errors
    
    def process_image_bytes(self, image_data: bytes, filename: str, content_type: str) -> dict:
        """Process image bytes and return image info"""
        return {
            "filename": filename,
            "content_type": content_type,
            "image_data": image_data,
            "file_size": len(image_data)
        }


if __name__ == "__main__":
    # Example usage
    ocr_service = OCRService()

    # Load an example image (replace with actual image bytes)
    with open("/Users/admin/Downloads/2022-05-09-110412-1.png", "rb") as f:
        image_bytes = f.read()

    extracted_text = ocr_service.extract_text(image_bytes)
    print(f"Extracted text: {extracted_text[:500]}...")  # Show first 500 chars