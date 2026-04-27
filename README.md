# Talenta Auto Login

Bot otomatis untuk clock in dan clock out di [Talenta (Mekari)](https://hr.talenta.co) menggunakan Selenium.

## Fitur

- Auto clock in saat script dijalankan (jika belum clock in hari itu)
- Auto clock out setelah jam yang ditentukan
- Tracking status harian via SQLite agar tidak duplikat
- Screenshot otomatis untuk bukti kehadiran
- Support headless mode untuk server/VPS
- Scheduler bawaan atau via cron/Task Scheduler

## Prasyarat

- Python 3.10+
- Google Chrome
- [ChromeDriver](https://chromedriver.chromium.org/) (sesuai versi Chrome)

## Instalasi

```bash
git clone https://github.com/daffaInsignia/talenta-auto-login.git
cd talenta-auto-login

python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

## Konfigurasi

Copy `.env.example` ke `.env` lalu isi kredensial:

```bash
cp .env.example .env
```

```env
TALENTA_EMAIL=email@company.com
TALENTA_PASSWORD=password_kamu
CLOCK_IN_TIME=09:00
CLOCK_OUT_TIME=18:00
HEADLESS=false
```

| Variable | Deskripsi | Default |
|---|---|---|
| `TALENTA_EMAIL` | Email login Talenta | (wajib) |
| `TALENTA_PASSWORD` | Password Talenta | (wajib) |
| `CLOCK_IN_TIME` | Jam clock in (HH:MM) | `09:00` |
| `CLOCK_OUT_TIME` | Jam clock out (HH:MM) | `18:00` |
| `HEADLESS` | Jalankan tanpa browser GUI | `false` |

## Penggunaan

### Manual

```bash
# Clock in
python main.py clock_in

# Clock out
python main.py clock_out
```

### Scheduler (loop terus-menerus)

```bash
# Cek setiap 5 menit, clock in/out otomatis
python scheduler.py

# Jalankan sekali saja (untuk cron)
python scheduler.py --once
```

### Setup Otomatis

**Windows** (Task Scheduler):
```
# Jalankan sebagai Administrator
setup_cron.bat
```

**Linux/macOS** (Crontab):
```bash
chmod +x setup_cron.sh
./setup_cron.sh
```

Keduanya akan menjadwalkan pengecekan setiap 5 menit.

## Struktur Project

```
talenta-auto-login/
├── main.py           # Login & klik tombol clock in/out
├── scheduler.py      # Scheduler & logika waktu
├── db.py             # SQLite tracking status harian
├── run.bat           # Runner script (Windows)
├── run.sh            # Runner script (Linux)
├── setup_cron.bat    # Setup Task Scheduler (Windows)
├── setup_cron.sh     # Setup crontab (Linux)
├── requirements.txt
├── .env.example
└── screenshots/      # Bukti screenshot otomatis
```

## License

MIT
