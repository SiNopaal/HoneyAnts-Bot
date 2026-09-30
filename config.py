import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Telegram API credentials (Telethon)
API_ID = int(os.getenv("API_ID", 2040))
API_HASH = os.getenv("API_HASH", "b18441a1ff607e10a989891a5462e627")

# Direktori sesi Telethon (Mendukung folder ./sessions atau custom path via env)
LOCAL_SESSION_FALLBACK = os.path.expanduser(r"~\OneDrive\Documents\New Session Tele")
SESSIONS_DIR = os.getenv("SESSIONS_DIR", LOCAL_SESSION_FALLBACK if os.path.exists(LOCAL_SESSION_FALLBACK) else os.path.join(BASE_DIR, "sessions"))


# Bot Target
BOT_USERNAME = "HoneyAntsBot"
START_PARAM = "ref_75FBM8"
BASE_URL = "https://honeyants.fun"

# Automation Features Toggle
AUTO_CLAIM_FREE_QUEEN = True     # Klaim ratu gratis pertama kali jika belum
AUTO_DAILY_REWARD = True         # Klaim bonus harian (daily streak)
AUTO_FREE_SPIN = True            # Putar roda keberuntungan gratis harian
AUTO_COLLECT_HONEY = True        # Panen balözü (madu) dari setiap koloni
AUTO_WATER_NEST = True           # Siram / jaga kelembaban koloni
AUTO_CLEAN_NEST = True           # Bersihkan makanan berjamur
AUTO_FEED_ANTS = True            # Beri makan koloni secara agresif agar cepat level up & power naik
AUTO_BUY_FOOD = True             # Beli makanan ulat/madu jika stok kosong (pakai AMBER)
AUTO_OPTIMIZE_CASTE = True       # Optimalkan rasio kasta tentara (Soldier/Asker) untuk power tempur maksimal
AUTO_JOIN_CLAN = True            # Masuk ke clan terbuka agar bisa serang Boss monster
AUTO_ATTACK_BOSS = True          # Serang Boss Monster clan setiap cooldown 2 jam selesai
AUTO_CLAIM_TASKS = True          # Klaim daily quests yang sudah selesai
AUTO_CLAIM_SOCIAL = True         # Buka dan klaim tugas sosial media
AUTO_CLAIM_GIFTS = True          # Klaim hadiah inbox
AUTO_CLAIM_REFERRAL = True       # Klaim komisi referral & tier milestone
AUTO_CLAIM_CLAN_CHEST = True     # Buka dan klaim Peti Harian Klan
AUTO_CLAIM_MILESTONES = True     # Klaim pencapaian milestone perkembangan koloni
AUTO_EXPEDITION = True           # Kirim ekspedisi & klaim hasil ekspedisi
AUTO_PVP_TRAIN = True            # Latihan perang pvp gratis harian

# Delays & Timing
DELAY_BETWEEN_ACCOUNTS_MIN = 3   # Detik minimal jeda antar akun
DELAY_BETWEEN_ACCOUNTS_MAX = 7   # Detik maksimal jeda antar akun
DELAY_BETWEEN_ACTIONS_MIN = 1.0  # Detik minimal jeda antar aksi
DELAY_BETWEEN_ACTIONS_MAX = 2.5  # Detik maksimal jeda antar aksi
LOOP_INTERVAL_HOURS = 2          # Interval loop otomatis (2 jam tepat sesuai cooldown Boss/Monster)


# Data File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data.txt")
PROXIES_FILE = os.path.join(BASE_DIR, "proxies.txt")
