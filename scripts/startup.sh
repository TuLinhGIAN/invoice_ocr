#!/bin/bash
set -e

echo "🚀 Starting OCR Invoice Service..."

# Create necessary directories
mkdir -p /tmp/torch /tmp/huggingface /tmp/transformers

echo "📥 Downloading Marker models..."
python /app/scripts/download_models.py

if [ $? -eq 0 ]; then
    echo "✅ Models downloaded successfully"
    echo "🌟 Starting FastAPI server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "❌ Model download failed"
    exit 1
fi