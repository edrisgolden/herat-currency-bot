import os
import re
import json
import requests
from pathlib import Path

TOKEN = os.environ["BOT_TOKEN"]
CHANNEL = "@Herat_chanil"
SOURCE = "https://t.me/s/nerkhYabkhorasanMarket"
STATE_FILE = Path("last_rates.json")

def get_rates():
response = requests.get(
SOURCE,
headers={"User-Agent": "Mozilla/5.0"},
timeout=30
)
response.raise_for_status()
html = response.text

rates = {}

patterns = {
    "کلدار": r"کلدار\s+به\s+افغانی\s*([0-9,.]+)\s*خرید\s*\|\s*([0-9,.]+)\s*فروش",
    "دالر": r"(?:دالر|دلار)\s+به\s+افغانی\s*([0-9,.]+)\s*خرید\s*\|\s*([0-9,.]+)\s*فروش",
    "تومان چک": r"تومان\s+چک\s+به\s+افغانی\s*([0-9,.]+)\s*خرید\s*\|\s*([0-9,.]+)\s*فروش",
    "تومان بانکی": r"تومان\s+بانکی\s+به\s+افغانی\s*([0-9,.]+)\s*خرید\s*\|\s*([0-9,.]+)\s*فروش",
}

for name, pattern in patterns.items():
    match = re.search(pattern, html, re.S)
    if not match:
        raise ValueError(f"نرخ پیدا نشد: {name}")
    rates[name] = [match.group(1), match.group(2)]

return rates

def send_message(text):
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
response = requests.post(
url,
data={"chat_id": CHANNEL, "text": text},
timeout=30
)
response.raise_for_status()
result = response.json()
if not result.get("ok"):
raise RuntimeError("ارسال پیام به تلگرام ناموفق بود")

def main():
rates = get_rates()

previous = {}
if STATE_FILE.exists():
    try:
        previous = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        previous = {}

messages = {
    "کلدار": f"هرات کلدار افغانی 🇵🇰 {rates['کلدار'][0]} خرید {rates['کلدار'][1]} فروش",
    "دالر": f"هرات دالر به افغانی💵 {rates['دالر'][0]} خـرید {rates['دالر'][1]} فـروش",
    "تومان چک": f"هرات تومان چک 💎 {rates['تومان چک'][0]} خرید {rates['تومان چک'][1]} فروش",
    "تومان بانکی": f"هرات تومان بانکی 💳 {rates['تومان بانکی'][0]} خرید {rates['تومان بانکی'][1]} فروش",
}

for name, message in messages.items():
    if previous.get(name) != rates[name]:
        send_message(message)

STATE_FILE.write_text(
    json.dumps(rates, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

if name == "main":
main()