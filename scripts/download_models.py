#!/usr/bin/env python3
"""
Script to download Marker models before starting the service
"""
import os
import sys
sys.path.append('/app')

from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.converters.pdf import PdfConverter

def download_models():
    """Download all required Marker models"""
    print("🔄 Starting model download...")
    
    try:
        # Set model cache directories
        os.environ['TORCH_HOME'] = '/tmp/torch'
        os.environ['HF_HOME'] = '/tmp/huggingface'
        os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers'
        
        print("📦 Creating model dictionary...")
        # This will download all required models
        model_dict = create_model_dict()
        print(f"✅ Model dictionary created with {len(model_dict)} models")
        
        # Configuration for Vietnamese invoice processing
        config = {
            "use_llm": False,
            "force_ocr": True,
            "format_lines": True,
            "redo_inline_math": False,
            "output_format": "json",
            "paginate_output": False,
            "disable_image_extraction": True,
        }
        
        print("⚙️ Initializing ConfigParser...")
        config_parser = ConfigParser(config)
        
        print("🏗️ Creating PdfConverter (this will ensure all models are loaded)...")
        # Initialize converter to ensure all models are loaded
        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=model_dict,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
        )
        
        print("✅ All models downloaded and loaded successfully!")
        print("🎉 Marker is ready for OCR processing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading models: {str(e)}")
        return False

if __name__ == "__main__":
    success = download_models()
    if success:
        print("🚀 Model download completed successfully")
        sys.exit(0)
    else:
        print("💥 Model download failed")
        sys.exit(1)