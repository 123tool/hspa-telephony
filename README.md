## 📞 HSPA Interactive Call & SMS Engine

Sebuah utilitas terminal (*CLI*) ringan, otomatis, dan interaktif untuk menghidupkan kembali perangkat keras broadband seluler USB HSPA/3G lama menjadi telepon meja *full-duplex*. Alat ini melewati batas perutean internet seluler standar dan mengubah desktop Linux Anda menjadi stasiun panggilan suara serta manajemen SMS menggunakan kredit kartu SIM lokal.

---

## 🔥 Fitur Utama

* **Penemuan Perangkat Keras Otomatis:** Mendeteksi indeks aktif `ModemManager` secara dinamis (Indeks `0`, `1`, dst.) tanpa perlu konfigurasi string manual yang rumit.
* **Penghubungan Audio Dupleks Penuh (*Full-Duplex Audio Bridge*):** Memanfaatkan saluran akustik `SoX` untuk menangkap dan mengonversi aliran audio telekomunikasi mentah (`u-law`, `8000Hz`, `mono`) antara jalur serial diagnostik (`/dev/ttyUSB1` & `/dev/ttyUSB2`) dengan mikrofon/speaker PC.
* **Normalisasi Nomor Cerdas:** Mengonversi struktur panggilan lokal secara otomatis (seperti format Indonesia `08xxxxxxxx`) menjadi standar internasional (`+62xxxxxxxx`) untuk memastikan keandalan *routing trunk* jaringan seluler.
* **Kontrol Siklus Hidup Volatil (*Volatil Lifecycle Control*):** Menyediakan, memicu, dan menghapus secara bersih objek panggilan serta pesan teks sekali pakai di dalam cache subsistem modem untuk mencegah penguncian sumber daya (*resource locking*).

---

## 🛠️ Panduan Instalasi & Persyaratan
​1. Prasyarat Sistem (OS Linux)
​Aplikasi ini membutuhkan beberapa perkakas sistem untuk memanipulasi port serial dan aliran audio mentah. Jalankan perintah berikut pada terminal Linux Anda (Debian/Ubuntu/Raspberry Pi OS) :
```
sudo apt update
sudo apt install -y sox libsox-fmt-all modemmanager cu screen python3-pip
```
2. Kloning / Siapkan Repositori
​Pastikan semua file proyek (engine.py, config.json, requirements.txt, dan run.sh) telah diletakkan dalam satu direktori yang sama.
​3. Konfigurasi Awal (config.json)
​Sesuaikan kode negara pada file config.json jika Anda berada di luar Indonesia :
```
{
  "country_code": "+62",
  "local_prefix": "0",
  "audio": {
    "sample_rate": 8000,
    "channels": 1,
    "format": "u-law"
  },
  "modem": {
    "fallback_audio_port": "/dev/ttyUSB1",
    "fallback_control_port": "/dev/ttyUSB2"
  }
}
```
