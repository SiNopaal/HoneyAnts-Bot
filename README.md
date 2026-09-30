# 🍯 HoneyAnts Bot Automation

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Telegram%20MiniApp-orange.svg)](https://t.me/HoneyAntsBot/app)

Bot multi-akun otomatis untuk Telegram MiniApp **HoneyAnts** (`https://t.me/HoneyAntsBot/app`). Dilengkapi dengan fitur penyerangan **Boss Monster otomatis setiap 2 jam**, pengoptimalan **Power Militer (Soldier Caste)**, perawatan koloni agresif, panen madu, upgrade sarang, dan klaim seluruh event/task harian.

---

## 🌟 Fitur Unggulan

- ⚔️ **Auto Boss Monster Raid (2-Hour Cooldown)**: Menyerang Boss Monster secara teratur setiap 2 jam untuk mendapatkan loot dan reward pool.
- 🛡️ **Auto Join Top Open Clan**: Otomatis bergabung ke Klan terbuka untuk membuka akses perburuan Boss dan bonus perang klan.
- 💥 **Power & Soldier Caste Boost**: Mengatur kasta militer (*Asker/Soldier 30%+*) untuk mendongkrak ATK Power dan damage kritikal ke monster.
- 🐛 **Aggressive Feeding & Stock Pakan**: Otomatis membeli & memberi pakan ulat (*kurt*) agar koloni cepat naik level, memicu kelahiran pasukan baru, dan menaikkan power secara pesat.
- 🏰 **Auto Equipment & Nest Upgrade**: Upgrade sarang (*Ytong Nest*) otomatis saat saldo AMBER mencukupi (+60 XP instan & melipatgandakan batas kapasitas pasukan).
- 📜 **Auto Battle Pass & Milestone Claims**: Mengklaim reward tier Battle Pass dan bonus pemula (*First Steps*).
- 👑 **Auto Free Queen Claim**: Otomatis mengklaim ratu gratis pertama kali jika akun baru.
- 🎓 **Auto Tutorial Completion**: Menyelesaikan tutorial pemula untuk bonus resource instan.
- 📅 **Auto Daily Streak**: Mengklaim bonus login harian berturut-turut.
- 🎡 **Auto Free Spin**: Putar roda keberuntungan harian gratis.
- 🍯 **Auto Colony Care**: Panen madu (*balözü*), siram sarang saat kelembaban turun, dan bersihkan jamur makanan.
- 📱 **Auto Daily Quests & Social Tasks**: Menyelesaikan quest harian & tugas media sosial.
- 🗺️ **Auto Expeditions**: Mengumpulkan hasil ekspedisi dan memberangkatkan ekspedisi baru.
- ⚔️ **Auto Free PVP Training**: Latihan perang koloni gratis harian.
- 🔄 **Dual Input Mode**: Mendukung pembacaan otomatis file `.session` Telethon maupun input manual `data.txt` (format fleksibel).
- 🌐 **Multi-Proxy Support**: Dukungan proxy HTTP/SOCKS5 via `proxies.txt`.

---

## 📂 Struktur Direktori

```text
honeyants-bot/
├── config.py             # Konfigurasi delay, toggle fitur, dan path
├── extract_sessions.py   # Ekstraktor Telethon session ke data.txt
├── api_client.py         # HTTP client & endpoint wrapper
├── bot_runner.py         # Workflow otomatis per akun
├── main.py               # CLI interaktif & continuous loop runner
├── data.example.txt      # Template format data akun
├── proxies.example.txt   # Template format proxy
├── requirements.txt      # Dependensi Python
├── .gitignore            # Proteksi keamanan data sensitif
└── README.md             # Dokumentasi penggunaan
```

---

## ⚙️ Instalasi

1. **Clone Repository**:
   ```bash
   git clone https://github.com/SiNopaal/HoneyAnts-Bot.git
   cd HoneyAnts-Bot
   ```

2. **Install Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 📝 Konfigurasi Akun

Anda dapat menggunakan salah satu dari dua cara berikut:

### Opsi A: Menggunakan File `.session` Telethon (Otomatis)
1. Letakkan file session Anda di folder session (sesuai path di `config.py`).
2. Jalankan script ekstraksi:
   ```bash
   python extract_sessions.py
   ```
   *Script akan otomatis mengambil `tgWebAppData` dan menyimpannya ke `data.txt`.*

### Opsi B: Menggunakan `data.txt` Manual
Buat file `data.txt` dan masukkan 1 akun per baris. Format yang didukung:
- **Raw InitData**:
  ```text
  query_id=AAF...&user=%7B%22id%22%3A...%7D&auth_date=...&hash=...
  ```
- **Full Webview URL**:
  ```text
  https://honeyants.fun/?tgWebAppStartParam=ref_75FBM8#tgWebAppData=user%3D...
  ```
- **Header Auth**:
  ```text
  tma user=%7B%22id%22%3A...
  ```

---

## 🚀 Menjalankan Bot

- **Menu Interaktif**:
  ```bash
  python main.py
  ```
- **Single Run (Sekali Jalan Semua Akun)**:
  ```bash
  python main.py --run
  ```
- **Mode Loop 24 Jam (Otomatis Tiap 2 Jam)**:
  ```bash
  python main.py --loop
  ```

---

## ⚠️ Disclaimer
Script ini dibuat untuk tujuan edukasi dan otomasi pribadi. Penggunaan bot merupakan tanggung jawab masing-masing pengguna.
