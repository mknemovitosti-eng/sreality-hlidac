import requests
import smtplib
from email.mime.text import MIMEText
import os
import re

URL = "https://www.sreality.cz/api/cs/v2/estates"

params = {
    "category_main_cb": 1,
    "category_type_cb": 1,
    "per_page": 20
}

r = requests.get(URL, params=params)

data = r.json()

results = []

# velmi hrubé benchmarky
MARKET_PRICES = {
    "praha": 140000,
    "brno": 120000,
    "ostrava": 65000,
    "plzen": 90000,
    "olomouc": 95000
}

for item in data["_embedded"]["estates"]:

    name = item.get("name", "")
    locality = item.get("locality", "")
    price = item.get("price", 0)

    # vytáhne m² z názvu
    match = re.search(r'(\d+)\s*m²', name)

    if not match:
        continue

    area = int(match.group(1))

    if area == 0:
        continue

    price_m2 = int(price / area)

    locality_lower = locality.lower()

    market_price = 100000

    for city, benchmark in MARKET_PRICES.items():
        if city in locality_lower:
            market_price = benchmark
            break

    discount = int(
        ((market_price - price_m2) / market_price) * 100
    )

    # jen zajímavé nabídky
    if discount < 20:
        continue

    hash_id = item.get("hash_id")

    seo = item.get("seo", {})
    seo_locality = seo.get("locality", "")

    link = (
        f"https://www.sreality.cz/detail/prodej/byt/"
        f"{seo_locality}/{hash_id}"
    )

    results.append(
        f"""
{name}

Lokalita: {locality}

Cena: {price:,} Kč
Plocha: {area} m²
Cena za m²: {price_m2:,} Kč

Pod trhem: {discount} %

{link}

----------------------------------------
"""
    )

if results:
    body = "\n".join(results)
else:
    body = "Žádné byty 20 % pod trhem nenalezeny."

msg = MIMEText(body)

msg["Subject"] = "Sreality investiční alert"
msg["From"] = os.environ["SMTP_USER"]
msg["To"] = os.environ["EMAIL_TO"]

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(
    os.environ["SMTP_USER"],
    os.environ["SMTP_PASSWORD"]
)

server.send_message(msg)

server.quit()
