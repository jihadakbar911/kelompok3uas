// Menunggu semua konten HTML dimuat sebelum menjalankan JavaScript
document.addEventListener('DOMContentLoaded', function() {

    // ===============================================================
    // FUNGSI UNTUK MENGAMBIL DATA & MENGGAMBAR GRAFIK PREDIKSI KOTA
    // ===============================================================
    async function muatGrafikPrediksiKota() {
        try {
            // Panggil API backend kita untuk data Prophet
            const response = await fetch('http://127.0.0.1:5000/api/prediksi-kota');
            const data = await response.json();

            // Siapkan data untuk Chart.js
            const labels = data.map(item => item.ds); // Tahun
            const prediksiUtama = data.map(item => item.yhat); // Garis biru
            const batasBawah = data.map(item => item.yhat_lower); // Batas area biru
            const batasAtas = data.map(item => item.yhat_upper); // Batas area biru

            const ctx = document.getElementById('grafik-prediksi-kota').getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Prediksi Volume Sampah (Ton)',
                        data: prediksiUtama,
                        borderColor: '#005f73',
                        backgroundColor: 'rgba(0, 95, 115, 0.1)',
                        fill: false, // Kita akan mengisi area secara manual
                        tension: 0.1
                    }, {
                        label: 'Rentang Prediksi',
                        data: batasAtas,
                        fill: 0, // Mengisi area dari dataset ini ke dataset di indeks 0
                        backgroundColor: 'rgba(148, 210, 189, 0.2)',
                        borderColor: 'transparent',
                        pointRadius: 0,
                    }, {
                        label: 'Batas Bawah', // Tidak perlu ditampilkan
                        data: batasBawah,
                        fill: 1, // Mengisi area dari dataset ini ke dataset di indeks 1
                        backgroundColor: 'rgba(148, 210, 189, 0.2)',
                        borderColor: 'transparent',
                        pointRadius: 0,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
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
            document.getElementById('prediksi-kota').innerHTML = '<p>Gagal memuat data grafik. Pastikan server backend berjalan.</p>';
        }
    }


    // ===============================================================
    // FUNGSI UNTUK MENGIRIM DATA FORM & MENAMPILKAN HASIL SIMULASI
    // ===============================================================
    const formSimulasi = document.getElementById('simulasi-form');
    const hasilContainer = document.getElementById('hasil-simulasi');

    formSimulasi.addEventListener('submit', async function(event) {
        // Mencegah form mengirim data dengan cara tradisional
        event.preventDefault();

        // Ambil data dari setiap input
        const dataUntukDikirim = {
            jumlah_botol: parseInt(document.getElementById('botol').value),
            jumlah_kantong: parseInt(document.getElementById('kantong').value),
            jumlah_bungkus: parseInt(document.getElementById('bungkus').value),
            daur_ulang: parseInt(document.getElementById('daur-ulang').value)
        };

        try {
            // Panggil API backend kita untuk klasifikasi KNN
            const response = await fetch('http://127.0.0.1:5000/api/simulasi-pribadi', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataUntukDikirim) // Kirim data sebagai JSON
            });

            const hasil = await response.json();

            // Tampilkan hasil di dalam div
            // Ambil lagi data angka dari form untuk perhitungan sederhana
const botol = parseInt(document.getElementById('botol').value);
const kantong = parseInt(document.getElementById('kantong').value);
const bungkus = parseInt(document.getElementById('bungkus').value);

// Kalkulasi sederhana (misal: total item per hari)
const totalItemPerHari = botol + kantong + bungkus;
// Estimasi total item hingga akhir 2026 (misal: sisa 500 hari)
const estimasiTotalItem = totalItemPerHari * 500;

// Tampilkan hasil gabungan
hasilContainer.innerHTML = `
    <h3>${hasil.gelar}</h3>
    <p>${hasil.deskripsi}</p>
    <hr>
    <p class="mt-3"><strong>Sebagai gambaran,</strong> dengan kebiasaan ini, kamu akan menghasilkan sekitar <strong>${estimasiTotalItem.toLocaleString('id-ID')} item</strong> sampah plastik hingga akhir tahun 2026.</p>
`;
            hasilContainer.style.display = 'block'; // Tampilkan container hasil

        } catch (error) {
            console.error('Gagal mengirim data simulasi:', error);
            hasilContainer.innerHTML = '<p>Gagal mendapatkan hasil. Pastikan server backend berjalan.</p>';
            hasilContainer.style.display = 'block';

        }
    });


    // Jalankan fungsi untuk memuat grafik saat halaman pertama kali dibuka
    muatGrafikPrediksiKota();

});