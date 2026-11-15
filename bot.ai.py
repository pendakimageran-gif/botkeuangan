import requests, re, os, time, threading
from datetime import datetime
from flask import Flask

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
FILE = "keuangan.txt"
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Keuangan Jalan! ✅"

def kirim(chat_id, teks):
    requests.post(f"{BASE}/sendMessage", json={"chat_id": chat_id, "text": teks}, timeout=5)

def catat(nama, harga):
    tgl = datetime.now().strftime("%d-%m-%Y %H:%M")
    with open(FILE, "a") as f:
        f.write(f"{tgl} | {nama} | {harga}\n")

def total_hari_ini():
    if not os.path.exists(FILE): return 0, []
    hari = datetime.now().strftime("%d-%m-%Y")
    total = 0; listnya = []
    for line in open(FILE).readlines():
        if hari in line:
            m = re.search(r"\| (\d+)", line)
            if m: total += int(m.group(1))
            listnya.append(line.strip())
    return total, listnya

def jalanin_bot():
    print("Bot Render jalan...")
    offset = 0
    while True:
        try:
            r = requests.get(f"{BASE}/getUpdates", params={"offset": offset, "timeout": 10}, timeout=15).json()
            for u in r.get("result", []):
                offset = u["update_id"] + 1
                msg = u.get("message", {})
                chat_id = msg.get("chat", {}).get("id")
                teks = msg.get("text", "").strip()
                if not teks or not chat_id: continue
                print("Dapat:", teks)
                low = teks.lower()
                if low == "/total":
                    t, l = total_hari_ini()
                    kirim(chat_id, f"Total jajan hari ini: Rp {t:,}\n\n" + "\n".join(l) if l else "Belum ada catatan")
                elif low == "/riwayat":
                    isi = open(FILE).read() if os.path.exists(FILE) else "Kosong"
                    kirim(chat_id, f"Riwayat:\n{isi[-1000:]}")
                elif low == "/start":
                    kirim(chat_id, "Bot cepet siap! Ketik `cilor 5000`")
                else:
                    m = re.match(r"([a-zA-Z ]+)\s*(\d+)", teks)
                    if m:
                        nama = m.group(1).strip().title()
                        harga = int(m.group(2))
                        catat(nama, harga)
                        t,_ = total_hari_ini()
                        kirim(chat_id, f"✅ Dicatet! {nama} Rp {harga:,}\nTotal hari ini: Rp {t:,}")
                    else:
                        kirim(chat_id, "Format: `cilor 5000`")
        except Exception as e:
            print("retry:", e)
            time.sleep(2)

threading.Thread(target=jalanin_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
