#!/bin/bash

# Pastikan script mati dengan bersih jika ditekan Ctrl+C
trap cleanup INT

cleanup() {
    echo -e "\n\n[*] Menghentikan sisa proses audio & membersihkan kunci serial..."
    sudo killall sox 2>/dev/null
    sudo systemctl restart ModemManager
    echo "[+] Selesai! Sistem aman kembali."
    exit 0
}

echo "[*] Menginstal dependensi python jika belum ada..."
pip3 install -r requirements.txt --break-system-packages 2>/dev/null

echo "[*] Mengonfigurasi hak akses port ttyUSB..."
sudo chmod o+rw /dev/ttyUSB* 2>/dev/null

# Jalankan engine utama dengan sudo
sudo python3 engine.py

# Panggil fungsi bersihkan saat keluar normal
cleanup
