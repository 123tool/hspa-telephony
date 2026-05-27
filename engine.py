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
        
    def send_sms(self, number, message):
        """Fitur Utama 4: Kontrol Siklus Hidup Volatil untuk SMS (Penyediaan & Penghapusan Bersih)"""
        clean_number = self.normalize_number(number)
        print(f"\n[*] Menyiapkan payload SMS ke {clean_number}...")
        
        # 1. Buat objek SMS kosong di subsistem modem
        create_out = self.run_cmd(f"mmcli -m {self.modem_index} --messaging-create-sms=\"number='{clean_number}',text='{message}'\"")
        match = re.search(re.compile(r'Successfully created SMS:\s*(.*)'), create_out)
        
        if not match:
            print("[X] Gagal membuat draf SMS di memori modem.")
            return False
            
        sms_path = match.group(1).strip()
        sms_id = sms_path.split('/')[-1]
        print(f"[+] SMS berhasil dialokasikan di cache dengan ID: {sms_id}")
        
        # 2. Kirim SMS yang berada di cache
        print("[*] Mengirimkan pesan melalui trunk seluler...")
        send_out = self.run_cmd(f"mmcli -s {sms_id} --send")
        
        if "successfully sent" in send_out.lower():
            print("[🔥] SMS Sukses Terkirim!")
            success = True
        else:
            print(f"[X] Gagal mengirim SMS. Respons: {send_out}")
            success = False
            
        # 3. Penghapusan Bersih (Volatile Cycle Purge) agar memori SIM/Modem tidak penuh
        print(f"[*] Membersihkan cache volatile untuk SMS ID: {sms_id}...")
        self.run_cmd(f"mmcli -m {self.modem_index} --messaging-delete-sms={sms_id}")
        print("[+] Memori volatile dibersihkan.")
        return success

    def make_call(self, number):
        """Membuat Panggilan Suara Keluar dengan Routing Otomatis"""
        clean_number = self.normalize_number(number)
        print(f"\n[*] Memulai panggilan keluar ke {clean_number}...")
        
        # Buat objek panggilan
        call_out = self.run_cmd(f"mmcli -m {self.modem_index} --voice-create-call=\"number='{clean_number}'\"")
        match = re.search(re.compile(r'Successfully created call:\s*(.*)'), call_out)
        
        if not match:
            print("[X] Gagal menginisialisasi jalur panggilan.")
            return
            
        call_path = match.group(1).strip()
        self.current_call_id = call_path.split('/')[-1]
        
        print(f"[+] Jalur panggilan terbentuk (ID: {self.current_call_id}). Menghubungi...")
        
        # Mulai jalankan audio routing (SoX) secara asynchronous
        audio_thread = threading.Thread(target=self.start_audio_routing)
        audio_thread.start()
        
        # Picu panggilan aktif
        self.run_cmd(f"mmcli -o {self.current_call_id} --start")
        
        input("\n[📞] Panggilan sedang berjalan. Tekan [ENTER] untuk mengakhiri panggilan...")
        
        # Hangup & bersihkan volatile object
        print("[*] Memutus panggilan...")
        self.run_cmd(f"mmcli -o {self.current_call_id} --hangup")
        self.stop_audio_routing()
        self.run_cmd(f"mmcli -m {self.modem_index} --voice-delete-call={self.current_call_id}")
        print("[+] Panggilan selesai dan dibersihkan.")

    def check_incoming_messages(self):
        """Memeriksa SMS Masuk secara berkala"""
        sms_list_out = self.run_cmd(f"mmcli -m {self.modem_index} --messaging-list-sms")
        # Parsing manual untuk list SMS
        lines = sms_list_out.split('\n')
        messages_data = []
        
        for line in lines:
            if "received" in line.lower():
                match = re.search(re.compile(r'/SMS/(\d+)'), line)
                if match:
                    idx = match.group(1)
                    info = self.run_cmd(f"mmcli -s {idx}")
                    
                    number = re.search(re.compile(r'number:\s*(.*)'), info)
                    text = re.search(re.compile(r'text:\s*(.*)'), info)
                    time_stamp = re.search(re.compile(r'timestamp:\s*(.*)'), info)
                    
                    num_str = number.group(1) if number else "Unknown"
                    text_str = text.group(1) if text else "(Pesan Kosong)"
                    time_str = time_stamp.group(1) if time_stamp else "Unknown"
                    
                    messages_data.append([idx, num_str, time_str, text_str])
                    
        if messages_data:
            print("\n📬 --- SMS MASUK BARU ---")
            print(tabulate(messages_data, headers=["ID", "Pengirim", "Waktu", "Pesan"], tablefmt="grid"))
            
            # Berikan opsi hapus setelah dibaca agar tidak menumpuk
            purge = input("\nApakah ingin mengosongkan inbox modem? (y/n): ")
            if purge.lower() == 'y':
                for msg in messages_data:
                    self.run_cmd(f"mmcli -m {self.modem_index} --messaging-delete-sms={msg[0]}")
                print("[+] Kotak masuk dibersihkan secara bersih!")
        else:
            print("\n📥 Kotak masuk kosong.")

    def interactive_menu(self):
        """Loop Menu Utama Antarmuka Terminal Pro"""
        if not self.detect_modem():
            return

        while True:
            print("\n" + "="*40)
            print(" MENU INTERAKTIF TELEFONI HSPA")
            print("="*40)
            print("1. 📞 Lakukan Panggilan Suara")
            print("2. ✉️  Kirim SMS Instan")
            print("3. 📥 Cek Kotak Masuk SMS")
            print("4. 🔄 Pindai Ulang Perangkat")
            print("5. ❌ Keluar")
            print("="*40)
            
            pilihan = input("Pilih menu (1-5): ").strip()
            
            if pilihan == "1":
                target = input("Masukkan nomor tujuan: ")
                if target: self.make_call(target)
            elif pilihan == "2":
                target = input("Masukkan nomor tujuan: ")
                pesan = input("Masukkan isi SMS: ")
                if target and pesan: self.send_sms(target, pesan)
            elif pilihan == "3":
                self.check_incoming_messages()
            elif pilihan == "4":
                self.detect_modem()
            elif pilihan == "5":
                print("\n[+] Mematikan mesin HSPA Telephony. Sampai jumpa!")
                break
            else:
                print("[!] Pilihan tidak valid, coba lagi.")

if __name__ == "__main__":
    # Proteksi hak akses root (diperlukan untuk manipulasi ttyUSB & mmcli direktif)
    if os.geteuid() != 0:
        print("[X] ERROR: Anda harus menjalankan script ini dengan hak akses 'sudo'!")
        print("    Contoh: sudo python3 engine.py")
        sys.exit(1)
        
    engine = HSPATelephonyEngine()
    engine.interactive_menu()
