FROM python:3.11.2-slim

WORKDIR /app

# Install dependencies sistem
RUN apt-get update && apt-get install -y \
    ffmpeg libsm6 libxext6 git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy semua file Flask langsung ke /app
COPY app/* ./

# ✅ Copy model dan tokenizer ke /app juga
COPY rnn_model.h5 .
COPY tokenizer.pkl .

EXPOSE 5000

# ✅ Jalankan app.py langsung dari root /app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
