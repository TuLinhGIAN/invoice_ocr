#!/usr/bin/env python3
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("🚀 Starting Invoice OCR API server...")
    print("📊 API will be available at: http://localhost:8000")
    print("📖 API docs will be available at: http://localhost:8000/docs")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)