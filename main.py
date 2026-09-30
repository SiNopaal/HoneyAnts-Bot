import os
import sys
import time
import random
import asyncio
class Fore:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    LIGHTBLACK_EX = "\033[90m"

class Style:
    RESET_ALL = "\033[0m"
    BRIGHT = "\033[1m"

import config
from bot_runner import BotRunner
from extract_sessions import extract_all


def banner():
    print(Fore.YELLOW + """
    ╔══════════════════════════════════════════════════════╗
    ║                 HONEYANTS AUTO BOT                   ║
    ║        Telegram MiniApp Multi-Account Farmer         ║
    ╚══════════════════════════════════════════════════════╝
    """ + Style.RESET_ALL)

import urllib.parse

def sanitize_init_data(raw: str) -> str:
    s = raw.strip()
    # Jika diawali tma 
    if s.lower().startswith("tma "):
        s = s[4:].strip()
    # Jika user menaruh full webview URL
    if s.startswith("http://") or s.startswith("https://"):
        if "#" in s:
            frag = s.split("#", 1)[1]
            params = dict(urllib.parse.parse_qsl(frag))
            if "tgWebAppData" in params:
                return params["tgWebAppData"]
        if "?" in s:
            query = s.split("?", 1)[1]
            params = dict(urllib.parse.parse_qsl(query))
            if "tgWebAppData" in params:
                return params["tgWebAppData"]
    # Jika user menaruh string yang ada tgWebAppData=...
    if "tgWebAppData=" in s:
        # cari nilai tgWebAppData
        parts = s.split("tgWebAppData=", 1)[1].split("&")[0]
        return urllib.parse.unquote(parts)
    return s

def load_accounts():
    if not os.path.exists(config.DATA_FILE):
        return []
    cleaned = []
    with open(config.DATA_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                clean_data = sanitize_init_data(line)
                if clean_data:
                    cleaned.append(clean_data)
    return cleaned


def load_proxies():
    if not os.path.exists(config.PROXIES_FILE):
        return []
    with open(config.PROXIES_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return lines

def run_all_accounts():
    accounts = load_accounts()
    if not accounts:
        print(Fore.RED + f"[-] Tidak ada akun di {config.DATA_FILE}. Melakukan ekstraksi otomatis dari sessions..." + Style.RESET_ALL)
        asyncio.run(extract_all())
        accounts = load_accounts()
        if not accounts:
            print(Fore.RED + "[-] Gagal mendapatkan data akun. Pastikan file session tersedia di " + config.SESSIONS_DIR + Style.RESET_ALL)
            return

    proxies = load_proxies()
    print(Fore.CYAN + f"[*] Memulai eksekusi untuk {len(accounts)} akun..." + Style.RESET_ALL)
    if proxies:
        print(Fore.CYAN + f"[*] Ditemukan {len(proxies)} proxies." + Style.RESET_ALL)
    print("="*65)

    success_count = 0
    for idx, init_data in enumerate(accounts, start=1):
        proxy = proxies[(idx - 1) % len(proxies)] if proxies else None
        runner = BotRunner(init_data, account_index=idx, proxy=proxy)
        try:
            ok = runner.run_account()
            if ok:
                success_count += 1
        except Exception as e:
            print(Fore.RED + f"[Akun #{idx}] [ERROR] Terjadi kesalahan: {e}" + Style.RESET_ALL)

        if idx < len(accounts):
            delay = random.uniform(config.DELAY_BETWEEN_ACCOUNTS_MIN, config.DELAY_BETWEEN_ACCOUNTS_MAX)
            print(Fore.LIGHTBLACK_EX + f"[-] Jeda {delay:.1f} detik menuju akun berikutnya..." + Style.RESET_ALL)
            time.sleep(delay)
        print("-" * 65)

    print(Fore.GREEN + f"\n[V] Selesai memproses {len(accounts)} akun ({success_count} sukses)." + Style.RESET_ALL)

def loop_mode():
    while True:
        banner()
        run_all_accounts()
        wait_seconds = config.LOOP_INTERVAL_HOURS * 3600
        print(Fore.CYAN + f"\n[*] Siklus selesai. Menunggu {config.LOOP_INTERVAL_HOURS} jam untuk siklus berikutnya..." + Style.RESET_ALL)
        try:
            for s in range(wait_seconds, 0, -1):
                hrs = s // 3600
                mins = (s % 3600) // 60
                secs = s % 60
                sys.stdout.write(f"\r{Fore.YELLOW}[TIMER] Siklus berikutnya dalam: {hrs:02d}:{mins:02d}:{secs:02d}{Style.RESET_ALL}")
                sys.stdout.flush()
                time.sleep(1)
            print("\n")
        except KeyboardInterrupt:
            print(Fore.RED + "\n[!] Mode loop dihentikan oleh pengguna." + Style.RESET_ALL)
            break

def main():
    banner()
    print("Pilih Mode Operasi:")
    print("1. Jalankan Sekali untuk Semua Akun (Single Run)")
    print("2. Jalankan Mode Otomatis 24 Jam (Continuous Loop)")
    print("3. Ekstrak Ulang Sesi Telegram ke data.txt (Telethon)")
    print("0. Keluar")
    print("-" * 50)
    
    choice = input("Masukkan pilihan [1-3]: ").strip()
    if choice == "1":
        run_all_accounts()
    elif choice == "2":
        loop_mode()
    elif choice == "3":
        asyncio.run(extract_all())
    elif choice == "0":
        print("Sampai jumpa!")
    else:
        print(Fore.RED + "Pilihan tidak valid." + Style.RESET_ALL)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--run", "-r", "run"]:
            run_all_accounts()
        elif arg in ["--loop", "-l", "loop"]:
            loop_mode()
        elif arg in ["--extract", "-e", "extract"]:
            asyncio.run(extract_all())
        else:
            main()
    else:
        main()
