## HSPA Interactive Call & SMS Engine

Sebuah utilitas terminal (*CLI*) ringan, otomatis, dan interaktif untuk menghidupkan kembali perangkat keras broadband seluler USB HSPA/3G lama menjadi telepon meja *full-duplex*. Alat ini melewati batas perutean internet seluler standar dan mengubah desktop Linux Anda menjadi stasiun panggilan suara serta manajemen SMS menggunakan kredit kartu SIM lokal.

---

## Fitur

* **Penemuan Perangkat Keras Otomatis:** Mendeteksi indeks aktif `ModemManager` secara dinamis (Indeks `0`, `1`, dst.) tanpa perlu konfigurasi string manual yang rumit.
* **Penghubungan Audio Dupleks Penuh (*Full-Duplex Audio Bridge*):** Memanfaatkan saluran akustik `SoX` untuk menangkap dan mengonversi aliran audio telekomunikasi mentah (`u-law`, `8000Hz`, `mono`) antara jalur serial diagnostik (`/dev/ttyUSB1` & `/dev/ttyUSB2`) dengan mikrofon/speaker PC.
* **Normalisasi Nomor Cerdas:** Mengonversi struktur panggilan lokal secara otomatis (seperti format Indonesia `08xxxxxxxx`) menjadi standar internasional (`+62xxxxxxxx`) untuk memastikan keandalan *routing trunk* jaringan seluler.
* **Kontrol Siklus Hidup Volatil (*Volatil Lifecycle Control*):** Menyediakan, memicu, dan menghapus secara bersih objek panggilan serta pesan teks sekali pakai di dalam cache subsistem modem untuk mencegah penguncian sumber daya (*resource locking*).

---

## Panduan Instalasi & Persyaratan

1. Prasyarat Sistem (OS Linux)
​Aplikasi ini membutuhkan beberapa perkakas sistem untuk memanipulasi port serial dan aliran audio mentah. Jalankan perintah berikut pada terminal Linux Anda (Debian/Ubuntu/Raspberry Pi OS) :
```
sudo apt update
sudo apt install -y sox libsox-fmt-all modemmanager cu screen python3-pip
```

2. Kloning / Siapkan Repositori
Pastikan semua file proyek (`engine.py`, `config.json`, `requirements.txt`, dan `run.sh`) telah diletakkan dalam satu direktori yang sama.

​3. Konfigurasi Awal (`config.json`)
​Sesuaikan kode negara pada file `config.json` jika Anda berada di luar Indonesia :
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

## Cara Menjalankan Aplikasi
- Hubungkan modem USB HSPA/3G Anda ke port USB komputer.
- Pastikan kartu SIM di dalam modem memiliki pulsa/kredit aktif untuk telepon dan SMS.
- Berikan hak akses eksekusi pada script wrapper :
  ```
  chmod +x run.sh
- Jalankan aplikasi dengan hak akses root menggunakan perintah :
  ```
  sudo ./run.sh


## Panduan Penggunaan Antarmuka (CLI)
​Setelah berhasil dijalankan, Anda akan dihadapkan dengan menu interaktif berbasis terminal :
```
========================================
 MENU INTERAKTIF TELEFONI HSPA
========================================
1. 📞 Lakukan Panggilan Suara
2. ✉️  Kirim SMS Instan
3. 📥 Cek Kotak Masuk SMS
4. 🔄 Pindai Ulang Perangkat
5. ❌ Keluar
========================================
Pilih menu (1-5):
```
​

⚠️ Catatan Penting Pembersihan Otomatis : 

> Setiap kali panggilan selesai atau SMS terkirim, aplikasi secara otomatis melakukan Purge (penghapusan total) pada objek memori internal modem. Hal ini menjamin ruang penyimpanan kartu SIM Anda tidak akan pernah penuh. Jika Anda keluar secara paksa menggunakan Ctrl+C, wrapper run.sh akan otomatis merestart service ModemManager untuk membebaskan kunci port serial.
