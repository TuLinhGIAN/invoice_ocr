FROM python:3.11-slim

# Install system dependencies for Marker and OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    poppler-utils \
    ghostscript \
    tesseract-ocr \
    tesseract-ocr-vie \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for better performance
ENV TORCH_HOME=/tmp/torch
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/transformers

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x /app/scripts/startup.sh /app/scripts/download_models.py

# Expose port
EXPOSE 8000

# Run the startup script
CMD ["/app/scripts/startup.sh"]