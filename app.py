# ===================================================================
# APLIKASI WEB FLASK - BACKEND UNTUK PREDIKSI SAMPAH (VERSI LENGKAP)
#
# Proyek UAS - Kecerdasan Buatan & Otomata dan Teori Bahasa
# ===================================================================

# ----------------------------------------------------
# 1. IMPORT LIBRARY YANG DIBUTUHKAN
# ----------------------------------------------------
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pandas as pd
import joblib  # Untuk memuat model .pkl
from prophet import Prophet
import os
import logging

logging.basicConfig(level=logging.INFO)


# ----------------------------------------------------
# 2. INISIALISASI APLIKASI FLASK
# ----------------------------------------------------
app = Flask(__name__)
CORS(app) # Mengizinkan akses dari domain lain (penting untuk development)


# -----------------------------------------------------------------------
# 3. MEMUAT MODEL MACHINE LEARNING SAAT SERVER PERTAMA KALI DIJALANKAN
#    Ini lebih efisien daripada memuat ulang setiap kali ada request
# -----------------------------------------------------------------------
try:
    model_knn = joblib.load('model_knn.pkl')
    scaler = joblib.load('scaler.pkl')
    print("✅ Model KNN dan Scaler berhasil dimuat saat startup.")
except FileNotFoundError:
    model_knn = None
    scaler = None
    print("⚠️ PERINGATAN: File 'model_knn.pkl' atau 'scaler.pkl' tidak ditemukan.")
    print("   Endpoint simulasi pribadi tidak akan berfungsi.")


# ----------------------------------------------------
# 4. ROUTE UNTUK HALAMAN UTAMA (HOMEPAGE)
#    Menampilkan file index.html dari folder /templates
# ----------------------------------------------------
@app.route('/')
def home():
    """Menyajikan halaman utama website."""
    return render_template('index.html')


# ---------------------------------------------------------------------
# 5. API ENDPOINT UNTUK MODEL #1 (PREDIKSI KOTA - PROPHET)
#    Dipanggil oleh JavaScript untuk mengisi data grafik
# ---------------------------------------------------------------------
@app.route('/api/prediksi-kota', methods=['GET'])
def get_city_prediction():
    """Menjalankan model Prophet dan mengembalikan hasil prediksi volume sampah kota."""
    try:
        # Memuat dataset dari file CSV
        df_sampah = pd.read_csv('jumlah_capaian_penanganan_sampah_di_kota_bandung.csv')
        df_penduduk = pd.read_csv('jumlah_penduduk_kota_bandung.csv')
        
        # Agregasi data sampah dari bulanan menjadi tahunan
        df_sampah_tahunan = df_sampah.groupby('tahun')['jumlah_sampah'].sum().reset_index()
        df_penduduk_clean = df_penduduk[['tahun', 'jumlah_penduduk']]
        
        # Gabungkan data sampah tahunan dan data penduduk
        df_gabungan = pd.merge(df_sampah_tahunan, df_penduduk_clean, on='tahun', how='inner').dropna()

        # Persiapan data untuk Prophet
        df_prophet = df_gabungan.rename(columns={'tahun': 'ds', 'jumlah_sampah': 'y'})
        df_prophet['ds'] = pd.to_datetime(df_prophet['ds'].astype(str) + '-12-31')

        # Latih model Prophet dengan regresor penduduk
        model_prophet = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
        model_prophet.add_regressor('jumlah_penduduk')
        model_prophet.fit(df_prophet)

        # Buat frame prediksi masa depan
        future = model_prophet.make_future_dataframe(periods=3, freq='YE')
        pertumbuhan_penduduk_rata2 = df_prophet['jumlah_penduduk'].diff().mean()
        populasi_terakhir = df_prophet['jumlah_penduduk'].iloc[-1]
        populasi_masa_depan = [populasi_terakhir + (pertumbuhan_penduduk_rata2 * i) for i in range(1, 4)]
        future['jumlah_penduduk'] = list(df_prophet['jumlah_penduduk']) + populasi_masa_depan
        
        # Lakukan prediksi
        forecast = model_prophet.predict(future)
        
        # Format hasil untuk dikirim sebagai JSON
        hasil_prediksi = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        hasil_prediksi['ds'] = hasil_prediksi['ds'].dt.strftime('%Y')
        
        return jsonify(hasil_prediksi.to_dict(orient='records'))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------------------
# 6. API ENDPOINT UNTUK MODEL #2 (KLASIFIKASI USER - KNN)
#    Menerima data dari form simulasi dan mengembalikan hasil klasifikasi
# ------------------------------------------------------------------------
@app.route('/api/simulasi-pribadi', methods=['POST'])
def get_personal_simulation():
    """Menerima input dari form, melakukan prediksi dengan model KNN, dan mengembalikan hasilnya."""
    if not model_knn or not scaler:
        return jsonify({"error": "Model klasifikasi tidak siap di server."}), 500
        
    try:
        # Ambil data JSON yang dikirim dari frontend
        data = request.get_json()
        
        # Susun data sesuai urutan fitur saat melatih model
        input_data = [[
            data['jumlah_botol'],
            data['jumlah_kantong'],
            data['jumlah_bungkus'],
            data['daur_ulang']
        ]]
        
        # Lakukan scaling pada data input menggunakan scaler yang sudah disimpan
        input_data_scaled = scaler.transform(input_data)
        
        # Lakukan prediksi menggunakan model KNN yang sudah disimpan
        prediksi_profil = model_knn.predict(input_data_scaled)
        hasil_profil = prediksi_profil[0]
        
        # Terjemahkan hasil teknis ('Rendah', 'Sedang', 'Tinggi') menjadi pesan menarik
        if hasil_profil == 'Rendah':
            gelar = "Jawara Lingkungan ✨"
            deskripsi = "Luar biasa! Kamu adalah inspirasi dalam menjaga bumi. Pertahankan kebiasaan baikmu!"
        elif hasil_profil == 'Sedang':
            gelar = "Pejuang Diet Plastik ⭐"
            deskripsi = "Sudah bagus! Kamu sudah di jalur yang benar. Tingkatkan sedikit lagi untuk jadi jawara!"
        else: # 'Tinggi'
            gelar = "Pemula Hijau 👍"
            deskripsi = "Perjalananmu baru dimulai! Ayo kurangi sampah plastik sedikit demi sedikit setiap hari."
            
        # Kirim hasilnya kembali ke frontend
        return jsonify({
            "gelar": gelar,
            "deskripsi": deskripsi
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------
# 7. MENJALANKAN SERVER FLASK
# ----------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
