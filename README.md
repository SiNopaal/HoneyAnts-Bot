# 🍯 HoneyAnts Bot Automation

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Telegram%20MiniApp-orange.svg)](https://t.me/HoneyAntsBot/app)

## Bot multi-akun otomatis untuk Telegram MiniApp **HoneyAnts** https://t.me/HoneyAntsBot/app?startapp=ref_75FBM8. 
Dilengkapi dengan fitur penyerangan **Boss Monster otomatis setiap 2 jam**, pengoptimalan **Power Militer (Soldier Caste)**, perawatan koloni agresif, panen madu, upgrade sarang, dan klaim seluruh event/task harian.

---

## 🌟 Fitur Unggulan

- ⏱️ **Dynamic Cooldown Synchronization**: Waktu jeda antar siklus otomatis menyesuaikan secara presisi dengan cooldown Boss Monster dan timer Ekspedisi di MiniApp (bukan sekadar timer kaku).
- ⚔️ **Auto Boss Monster Raid**: Menyerang Boss Monster secara otomatis saat cooldown server selesai untuk akumulasi damage dan reward pool.
- 🛡️ **Smart Clan Join & Requests**: Otomatis memindai klan terbuka dengan slot kosong yang sesuai dengan power koloni, atau mengirimkan request bergabung secara cerdas.
- 🎁 **Daily Clan Chest & Clan War Claims**: Membuka Peti Harian Klan setiap hari dan mengklaim reward akhir perang klan (*Clan War*).
- 💥 **Military Caste & Power Optimization**: Mengatur proporsi kasta militer (*Asker/Soldier 30%+*) untuk memaksimalkan ATK Power dan kritikal tempur.
- 🐛 **Aggressive Dual Feeding**: Membeli & memberikan pakan ulat (*kurt* untuk protein & pasukan) dan madu (*bal* untuk energi stamina) agar koloni cepat naik level.
- 🐜 **Live Prey Hunting & Nest Cleaning**: Mengklaim hasil buruan serangga hidup (+15 XP instan & progress quest) serta membersihkan sisa makanan berjamur.
- 🏰 **Auto Equipment & Nest Upgrade**: Upgrade sarang (*Ytong Nest*) otomatis saat saldo AMBER mencukupi untuk melipatgandakan batas kapasitas pasukan.
- 🏆 **Auto Milestones & Referral Tier Claims**: Mengklaim pencapaian milestone ekosistem serta tier reward undangan teman.
- 📜 **Auto Battle Pass & Milestone Claims**: Mengklaim reward tier Battle Pass dan bonus pemula (*First Steps*).
- 👑 **Auto Free Queen Claim**: Otomatis mengklaim ratu gratis pertama kali jika akun baru.
- 🎓 **Auto Tutorial Completion**: Menyelesaikan tutorial pemula untuk bonus resource instan.
- 📅 **Auto Daily Streak**: Mengklaim bonus login harian berturut-turut.
- 🎡 **Auto Free Spin**: Putar roda keberuntungan harian gratis.
- 🍯 **Auto Colony Care**: Panen madu (*balözü*), siram sarang saat kelembaban turun, dan pemeliharaan koloni.
- 📱 **Auto Daily Quests & Social Tasks**: Menyelesaikan quest harian & tugas media sosial.
- 🗺️ **Auto Expeditions**: Menghitung kebutuhan pekerja dan memberangkatkan ekspedisi serta mengumpulkan hasilnya.
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
1. Letakkan file `.session` akun Anda di folder `sessions/` (atau atur `SESSIONS_DIR` di file `config.py`).
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
