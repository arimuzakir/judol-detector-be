from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tempfile, easyocr, pickle, os, whisper
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# ====== Load model ======
MODEL_PATH = os.path.abspath("rnn_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)

os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"
modelWhisper = whisper.load_model("base")

# ====== Load tokenizer ======
TOKENIZER_PATH = os.path.abspath("tokenizer.pkl")
with open(TOKENIZER_PATH, 'rb') as f:
    tokenizer = pickle.load(f)

MAX_SEQUENCE_LENGTH = 100 

# ====== Init EasyOCR  ======
reader = easyocr.Reader(['id', 'en'])

# ====== Preprocess Text Function ======
def preprocess_text(text):
    sequence = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(sequence, maxlen=MAX_SEQUENCE_LENGTH, padding="post", truncating="post")
    return padded

@app.route('/', methods=['GET'])
def index():
    return "Running";

# ====== Endpoint untuk teks langsung ======
@app.route('/api/detect-text', methods=['POST'])
def detect_text():
    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'Text tidak boleh kosong'}), 400

    processed = preprocess_text(text)
    prediction = model.predict(processed)[0][0]

    result = {
        'status': 'Terdeteksi Iklan Judi' if prediction > 0.5 else 'Tidak Terindikasi Iklan Judi',
        'confidence': f'{prediction * 100:.2f}%',
        'raw_confidence': float(prediction)
    }

    return jsonify(result)

# ====== Endpoint untuk gambar dengan OCR ======
@app.route('/api/detect-image', methods=['POST'])
def detect_image():
    if 'image' not in request.files:
        return jsonify({'error': 'File gambar tidak ditemukan'}), 400

    image_file = request.files['image']
    image_bytes = image_file.read()

    # OCR menggunakan easyocr
    ocr_result = reader.readtext(image_bytes, detail=0)
    extracted_text = ' '.join(ocr_result)

    if not extracted_text.strip():
        return jsonify({'error': 'Teks tidak ditemukan di dalam gambar'}), 400

    # Prediksi
    processed = preprocess_text(extracted_text)
    prediction = model.predict(processed)[0][0]

    result = {
        'ocr_text': extracted_text,
        'status': 'Terdeteksi Iklan Judi' if prediction > 0.5 else 'Tidak Terindikasi Iklan Judi',
        'confidence': f'{prediction * 100:.2f}%',
        'raw_confidence': float(prediction)
    }

    return jsonify(result)

# ====== Endpoint untuk video ======
@app.route('/api/detect-video', methods=['POST'])
def detect_video():
    file = request.files.get('video')
    if not file:
        return jsonify({"status": "error", "message": "Tidak ada file di request"}), 400

    filename = secure_filename(file.filename)

    # Simpan sementara di /tmp
    with tempfile.NamedTemporaryFile(delete=False, dir="/tmp", suffix=os.path.splitext(filename)[1]) as tmp:
        temp_path = tmp.name
        file.save(temp_path)

    # Transkripsi
    print(f"🎥 Memproses: {filename}")
    result = modelWhisper.transcribe(temp_path)
    text_hasil = result["text"]
    print(f"✅ Selesai: {filename}")

    # Hapus file sementara
    os.remove(temp_path)

    # Prediksi
    processed = preprocess_text(text_hasil)
    prediction = model.predict(processed)[0][0]

    result = {
        'ocr_text': text_hasil,
        'status': 'Terdeteksi Iklan Judi' if prediction > 0.5 else 'Tidak Terindikasi Iklan Judi',
        'confidence': f'{prediction * 100:.2f}%',
        'raw_confidence': float(prediction)
    }

    return jsonify(result)
    
if __name__ == '__main__':
    app.run()


