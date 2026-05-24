import requests
import smtplib
from email.mime.text import MIMEText
import os

URL = "https://www.sreality.cz/api/cs/v2/estates"

params = {
    "category_main_cb": 1,   # byty
    "category_type_cb": 1,   # prodej
    "per_page": 20
}

r = requests.get(URL, params=params)

data = r.json()

results = []

for item in data["_embedded"]["estates"]:

    name = item.get("name", "")
    price = item.get("price", 0)

    area = item.get("usable_area", 0)

    if not area:
        continue

    price_m2 = int(price / area)

    locality = item.get("locality", "Neznámá lokalita")

    link = item.get("url", "")

    if not link:
        hash_id = item.get("hash_id", "")
        link = f"https://www.sreality.cz/detail/{hash_id}"

    results.append(
        f"""
{name}

Lokalita: {locality}

Cena: {price:,} Kč
Plocha: {area} m²
Cena za m²: {price_m2:,} Kč

{link}

----------------------------------------
"""
    )

if results:

    body = "\n".join(results)

else:

    body = "Žádné nové výsledky."

msg = MIMEText(body)

msg["Subject"] = "Sreality alert"
msg["From"] = os.environ["SMTP_USER"]
msg["To"] = os.environ["EMAIL_TO"]

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(
    os.environ["SMTP_USER"],
    os.environ["SMTP_PASSWORD"]
)

server.send_message(msg)

server.quit()
