from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import joblib
import json
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

try:
    model_knn = joblib.load('model_knn.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✅ Model KNN dan Scaler berhasil dimuat.")
except Exception as e:
    model_knn = None
    scaler = None
    print(f"⚠️ Gagal memuat model: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/prediksi-kota', methods=['GET'])
def get_city_prediction():
    try:
        # Hanya membaca file JSON yang sudah jadi
        with open('static/prophet_forecast.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/simulasi-pribadi', methods=['POST'])
def get_personal_simulation():
    # ... (logika KNN tidak berubah) ...
    if not model_knn or not scaler:
        return jsonify({"error": "Model klasifikasi tidak siap."}), 500
    try:
        data = request.get_json()
        input_data = [[data['jumlah_botol'], data['jumlah_kantong'], data['jumlah_bungkus'], data['daur_ulang']]]
        input_data_scaled = scaler.transform(input_data)
        hasil_profil = model_knn.predict(input_data_scaled)[0]
        
        if hasil_profil == 'Rendah':
            gelar = "Jawara Lingkungan ✨"
            deskripsi = "Luar biasa! Kamu adalah inspirasi dalam menjaga bumi."
        elif hasil_profil == 'Sedang':
            gelar = "Pejuang Diet Plastik ⭐"
            deskripsi = "Sudah bagus! Kamu sudah di jalur yang benar."
        else:
            gelar = "Pemula Hijau 👍"
            deskripsi = "Perjalananmu baru dimulai! Ayo kurangi sampah plastik."
            
        return jsonify({"gelar": gelar, "deskripsi": deskripsi})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
