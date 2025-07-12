document.addEventListener('DOMContentLoaded', function() {
    async function muatGrafikPrediksiKota() {
        try {
            // Menggunakan path relatif yang benar
            const response = await fetch('/api/prediksi-kota'); 
            const data = await response.json();
            // ... sisa kode grafik ...
            const ctx = document.getElementById('grafik-prediksi-kota').getContext('2d');
            new Chart(ctx, { /* ... konfigurasi chart ... */ });
        } catch (error) { console.error('Gagal memuat data grafik:', error); }
    }

    const formSimulasi = document.getElementById('simulasi-form');
    formSimulasi.addEventListener('submit', async function(event) {
        event.preventDefault();
        const dataUntukDikirim = { /* ... data form ... */ };
        try {
            // Menggunakan path relatif yang benar
            const response = await fetch('/api/simulasi-pribadi', { /* ... konfigurasi POST ... */ });
            const hasil = await response.json();
            // ... sisa kode untuk menampilkan hasil ...
        } catch (error) { console.error('Gagal mengirim data simulasi:', error); }
    });
    muatGrafikPrediksiKota();
});