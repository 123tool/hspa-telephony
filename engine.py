#!/usr/bin/env python3
import os
import sys
import json
import time
import subprocess
import re
import threading
from tabulate import tabulate

class HSPATelephonyEngine:
    def __init__(self):
        self.config = self.load_config()
        self.modem_index = None
        self.audio_process_in = None
        self.audio_process_out = None
        self.is_in_call = False
        
        print("="*60)
        print("🚀 HSPA INTERACTIVE CALL & SMS ENGINE v1.0")
        print("="*60)

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                return json.load(f)
        return {
            "country_code": "+62",
            "local_prefix": "0",
            "audio": {"sample_rate": 8000, "channels": 1, "format": "u-law"},
            "modem": {"fallback_audio_port": "/dev/ttyUSB1", "fallback_control_port": "/dev/ttyUSB2"}
        }

    def run_cmd(self, cmd):
        """Menjalankan perintah shell dan mengembalikan outputnya"""
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def detect_modem(self):
        """Fitur Utama 1: Penemuan Perangkat Keras Otomatis via ModemManager"""
        print("[*] Memindai perangkat modem HSPA...")
        mmcli_out = self.run_cmd("mmcli -L")
        
        # Mencari indeks modem seperti /org/freedesktop/ModemManager1/Modem/0
        match = re.search(re.compile(r'/Modem/(\d+)'), mmcli_out)
        if match:
            self.modem_index = match.group(1)
            print(f"[+] Modem ditemukan pada Indeks: {self.modem_index}")
            
            # Ambil detail informasi modem
            modem_info = self.run_cmd(f"mmcli -m {self.modem_index}")
            model = re.search(re.compile(r'model:\s*(.*)'), modem_info)
            status = re.search(re.compile(r'state:\s*(.*)'), modem_info)
            
            print(f"    👉 Model : {model.group(1) if model else 'Generic HSPA'}")
            print(f"    👉 Status: {status.group(1) if status else 'Unknown'}")
            return True
        else:
            print("[X] Gagal mendeteksi Modem via ModemManager.")
            print("    Pastikan modem dicolok dan service modemmanager berjalan (`sudo systemctl restart ModemManager`)")
            return False

    def normalize_number(self, number):
        """Fitur Utama 3: Normalisasi Nomor Cerdas (e.g., 0812 -> +62812)"""
        number = number.replace("-", "").replace(" ", "")
        prefix = self.config["local_prefix"]
        cc = self.config["country_code"]
        
        if number.startswith(prefix):
            return cc + number[len(prefix):]
        elif number.startswith("+"):
            return number
        else:
            return cc + number

    def start_audio_routing(self):
        """Fitur Utama 2: Penghubungan Audio Dupleks Penuh via SoX"""
        if self.is_in_call:
            return

        audio_port = self.config["modem"]["fallback_audio_port"]
        if not os.path.exists(audio_port):
            print(f"[!] Port audio mentah ({audio_port}) tidak ditemukan. Melewati routing audio.")
            return

        print(f"[*] Mengaktifkan Full-Duplex Audio Bridge di {audio_port}...")
        self.is_in_call = True

        # Alur 1: Mikrofon PC -> Mengonversi ke u-law 8kHz -> Kirim ke Modem (TX)
        # Menggunakan 'sox -d' untuk mengambil input default mic PC
        cmd_tx = f"sox -t alsa default -t raw -r 8000 -c 1 -e u-law {audio_port} 2>/dev/null"
        
        # Alur 2: Modem (RX Audio Mentah) -> Mengonversi dari u-law 8kHz -> Speaker PC
        cmd_rx = f"sox -t raw -r 8000 -c 1 -e u-law {audio_port} -t alsa default 2>/dev/null"

        self.audio_process_in = subprocess.Popen(cmd_tx, shell=True)
        self.audio_process_out = subprocess.Popen(cmd_rx, shell=True)
        print("[+] Audio Bridge aktif! Silakan berbicara melalui mikrofon PC Anda.")

    def stop_audio_routing(self):
        """Menghentikan proses audio bridging secara bersih"""
        print("[*] Mematikan Audio Bridge...")
        if self.audio_process_in:
            self.audio_process_in.terminate()
            self.audio_process_in = None
        if self.audio_process_out:
            self.audio_process_out.terminate()
            self.audio_process_out = None
        self.is_in_call = False
        print("[+] Audio Bridge dihentikan.")
