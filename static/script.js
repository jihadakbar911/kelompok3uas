// Menunggu semua konten HTML dimuat sebelum menjalankan JavaScript
document.addEventListener('DOMContentLoaded', function() {

    // ===============================================================
    // FUNGSI UNTUK MENGAMBIL DATA & MENGGAMBAR GRAFIK PREDIKSI KOTA
    // (VERSI BARU YANG LEBIH CEPAT)
    // ===============================================================
    async function muatGrafikPrediksiKota() {
        try {
            // Langsung memuat file JSON statis dari folder static.
            // Ini jauh lebih cepat daripada memanggil API yang harus melatih ulang model.
            const response = await fetch("{{ url_for('static', filename='prophet_forecast.json') }}");
            const data = await response.json();

            // Siapkan data untuk Chart.js
            const labels = data.map(item => item.ds);
            const prediksiUtama = data.map(item => item.yhat);
            const batasBawah = data.map(item => item.yhat_lower);
            const batasAtas = data.map(item => item.yhat_upper);

            const ctx = document.getElementById('grafik-prediksi-kota').getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Prediksi Volume Sampah (Ton)',
                        data: prediksiUtama,
                        borderColor: '#005f73',
                        tension: 0.1
                    }, {
                        label: 'Rentang Prediksi',
                        data: batasAtas,
                        fill: '+1', // Mengisi area dari dataset ini ke dataset di bawahnya
                        backgroundColor: 'rgba(148, 210, 189, 0.2)',
                        borderColor: 'transparent',
                        pointRadius: 0,
                    }, {
                        label: 'Batas Bawah', // Tidak perlu ditampilkan
                        data: batasBawah,
                        fill: '-1', // Mengisi area dari dataset ini ke dataset di atasnya
                        backgroundColor: 'rgba(148, 210, 189, 0.2)',
                        borderColor: 'transparent',
                        pointRadius: 0,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        },
                        legend: {
                            display: false // Sembunyikan legenda agar lebih bersih
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: false,
                            title: { display: true, text: 'Volume Sampah (Ton)' }
                        },
                        x: {
                            title: { display: true, text: 'Tahun' }
                        }
                    }
                }
            });

        } catch (error) {
            console.error('Gagal memuat data grafik:', error);
            document.getElementById('prediksi-kota').innerHTML = '<p>Gagal memuat data grafik. Pastikan file prediksi ada dan server berjalan.</p>';
        }
    }


    // ===============================================================
    // FUNGSI UNTUK MENGIRIM DATA FORM & MENAMPILKAN HASIL SIMULASI
    // (Tidak ada perubahan di bagian ini)
    // ===============================================================
    const formSimulasi = document.getElementById('simulasi-form');
    const hasilContainer = document.getElementById('hasil-simulasi');

    formSimulasi.addEventListener('submit', async function(event) {
        event.preventDefault();
        const dataUntukDikirim = {
            jumlah_botol: parseInt(document.getElementById('botol').value),
            jumlah_kantong: parseInt(document.getElementById('kantong').value),
            jumlah_bungkus: parseInt(document.getElementById('bungkus').value),
            daur_ulang: parseInt(document.getElementById('daur-ulang').value)
        };

        try {
            const response = await fetch('http://127.0.0.1:5000/api/simulasi-pribadi', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataUntukDikirim)
            });
            const hasil = await response.json();
            
            hasilContainer.innerHTML = `
                <h3>${hasil.gelar}</h3>
                <p>${hasil.deskripsi}</p>
            `;
            hasilContainer.style.display = 'block';

        } catch (error) {
            console.error('Gagal mengirim data simulasi:', error);
            hasilContainer.innerHTML = '<p>Gagal mendapatkan hasil. Pastikan server backend berjalan.</p>';
            hasilContainer.style.display = 'block';
        }
    });

    // Jalankan fungsi untuk memuat grafik saat halaman pertama kali dibuka
    muatGrafikPrediksiKota();
});