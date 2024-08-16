import time
import os
import sys
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Konfigurasi
ODOO_PATH = "/opt/odoo17/odoo17/odoo-bin" # Path odoo-bin
ODOO_CONF = "/etc/odoo17.conf" # Path Odoo config
ADDONS_PATH = "/opt/odoo17/addons" # Path Custom Addons
DB = "" # Nama DB yang digunakan
MODULES = ""  # Daftar modul yang akan di-upgrade, pisahkan dengan koma jika lebih dari satu

def start_odoo():
    print("Memulai Odoo...")
    subprocess.Popen([
        "python3", ODOO_PATH,
        "-c", ODOO_CONF,
        "--database", DB,
        "--update", MODULES
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)  # Tunggu beberapa detik agar Odoo siap
    print("Odoo telah dimulai.")

def restart_and_upgrade_odoo():
    print("Menghentikan Odoo...")
    subprocess.run(["pkill", "-f", ODOO_PATH])
    time.sleep(2)
    start_odoo()
    print("Odoo telah di-restart dan modul telah di-upgrade.")

class CustomHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        elif event.event_type in ['created', 'modified', 'deleted']:
            print(f"\nPerubahan terdeteksi: {event.src_path}")
            print("Memulai proses restart dan upgrade...")
            restart_and_upgrade_odoo()
            print("Proses selesai. Menunggu perubahan berikutnya...\n")

if __name__ == "__main__":
    print("===Odoo Auto Reload===")

    # Memulai Odoo
    start_odoo()

    event_handler = CustomHandler()
    observer = Observer()
    observer.schedule(event_handler, ADDONS_PATH, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nOdoo Auto Reload Stopped...")
        subprocess.run(["pkill", "-f", ODOO_PATH])
        observer.stop()
    observer.join()
    print("Program dihentikan.")
