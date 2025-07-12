# File: generate_prophet_data.py
import pandas as pd
from prophet import Prophet
import json

print("Memulai proses pra-kalkulasi data Prophet...")

df_sampah = pd.read_csv('jumlah_capaian_penanganan_sampah_di_kota_bandung.csv')
df_penduduk = pd.read_csv('jumlah_penduduk_kota_bandung.csv')
df_sampah_tahunan = df_sampah.groupby('tahun')['jumlah_sampah'].sum().reset_index()
df_penduduk_clean = df_penduduk[['tahun', 'jumlah_penduduk']]
df_gabungan = pd.merge(df_sampah_tahunan, df_penduduk_clean, on='tahun', how='inner').dropna()
df_prophet = df_gabungan.rename(columns={'tahun': 'ds', 'jumlah_sampah': 'y'})
df_prophet['ds'] = pd.to_datetime(df_prophet['ds'].astype(str) + '-12-31')

model_prophet = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=False)
model_prophet.add_regressor('jumlah_penduduk')
model_prophet.fit(df_prophet)

future = model_prophet.make_future_dataframe(periods=3, freq='YE')
pertumbuhan_penduduk_rata2 = df_prophet['jumlah_penduduk'].diff().mean()
populasi_terakhir = df_prophet['jumlah_penduduk'].iloc[-1]
populasi_masa_depan = [populasi_terakhir + (pertumbuhan_penduduk_rata2 * i) for i in range(1, 4)]
future['jumlah_penduduk'] = list(df_prophet['jumlah_penduduk']) + populasi_masa_depan
forecast = model_prophet.predict(future)

hasil_prediksi = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
hasil_prediksi['ds'] = hasil_prediksi['ds'].dt.strftime('%Y')
data_to_save = hasil_prediksi.to_dict(orient='records')

# Simpan hasilnya ke dalam folder static
with open('static/prophet_forecast.json', 'w') as f:
    json.dump(data_to_save, f)

print("✅ Berhasil! File 'prophet_forecast.json' telah dibuat di dalam folder 'static'.")