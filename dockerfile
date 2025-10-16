# Gunakan Python versi spesifik
FROM python:3.11.2-slim

WORKDIR /app

# Install system dependencies untuk ffmpeg, Whisper, EasyOCR, dll
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements dan install dependency Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code Flask app
COPY app ./app
COPY rnn_model.h5 .
COPY tokenizer.pkl .

# Expose port Flask
EXPOSE 8080

# Jalankan aplikasi
CMD ["python", "app/app.py"]
