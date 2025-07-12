# ===================================================================
# APLIKASI WEB FLASK - BACKEND UNTUK PREDIKSI SAMPAH
# VERSI FINAL DENGAN PRA-KALKULASI PROPHET
# ===================================================================

# 1. IMPORT LIBRARY YANG DIBUTUHKAN
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import joblib
import json # Tambahkan import json
import os
import logging

logging.basicConfig(level=logging.INFO)

# 2. INISIALISASI APLIKASI FLASK
app = Flask(__name__)
CORS(app)

# 3. MEMUAT MODEL MACHINE LEARNING SAAT SERVER PERTAMA KALI DIJALANKAN
try:
    model_knn = joblib.load('model_knn.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✅ Model KNN dan Scaler berhasil dimuat saat startup.")
except FileNotFoundError:
    model_knn = None
    scaler = None
    print("⚠️ PERINGATAN: File model atau scaler tidak ditemukan.")

# 4. ROUTE UNTUK HALAMAN UTAMA (HOMEPAGE)
@app.route('/')
def home():
    """Menyajikan halaman utama website."""
    return render_template('index.html')

# ===================================================================
# 5. API ENDPOINT UNTUK MODEL #1 (PREDIKSI KOTA - PROPHET)
#    (VERSI BARU YANG JAUH LEBIH CEPAT)
# ===================================================================
@app.route('/api/prediksi-kota', methods=['GET'])
def get_city_prediction():
    """Membaca file JSON yang sudah berisi data prediksi Prophet."""
    try:
        # Hanya membuka file statis yang sudah dibuat sebelumnya.
        # Proses ini sangat cepat dan ringan untuk server.
        with open('static/prophet_forecast.json', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "File prediksi (prophet_forecast.json) tidak ditemukan di server."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===================================================================
# 6. API ENDPOINT UNTUK MODEL #2 (KLASIFIKASI USER - KNN)
#    (Tidak ada perubahan di bagian ini)
# ===================================================================
@app.route('/api/simulasi-pribadi', methods=['POST'])
def get_personal_simulation():
    """Menerima input dari form, melakukan prediksi dengan model KNN, dan mengembalikan hasilnya."""
    if not model_knn or not scaler:
        return jsonify({"error": "Model klasifikasi tidak siap di server."}), 500
        
    try:
        data = request.get_json()
        input_data = [[
            data['jumlah_botol'],
            data['jumlah_kantong'],
            data['jumlah_bungkus'],
            data['daur_ulang']
        ]]
        input_data_scaled = scaler.transform(input_data)
        prediksi_profil = model_knn.predict(input_data_scaled)
        hasil_profil = prediksi_profil[0]
        
        if hasil_profil == 'Rendah':
            gelar = "Jawara Lingkungan ✨"
            deskripsi = "Luar biasa! Kamu adalah inspirasi dalam menjaga bumi. Pertahankan kebiasaan baikmu!"
        elif hasil_profil == 'Sedang':
            gelar = "Pejuang Diet Plastik ⭐"
            deskripsi = "Sudah bagus! Kamu sudah di jalur yang benar. Tingkatkan sedikit lagi untuk jadi jawara!"
        else:
            gelar = "Pemula Hijau 👍"
            deskripsi = "Perjalananmu baru dimulai! Ayo kurangi sampah plastik sedikit demi sedikit setiap hari."
            
        return jsonify({
            "gelar": gelar,
            "deskripsi": deskripsi
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 7. MENJALANKAN SERVER FLASK
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))