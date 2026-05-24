import requests
import smtplib
from email.mime.text import MIMEText
import os

URL = "https://www.sreality.cz/api/cs/v2/estates"

params = {
    "category_main_cb": 1,
    "category_type_cb": 1,
    "locality": "Praha",
    "per_page": 10
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

    price_m2 = price / area

    # velmi hrubý průměr Praha
    market_price_m2 = 140000

    discount = (
        (market_price_m2 - price_m2)
        / market_price_m2
    ) * 100

    if discount < 20:
        continue

    link = item.get("url", "")

    results.append(
        f"""
{name}

Cena: {price:,} Kč
Plocha: {area} m²
Cena/m²: {int(price_m2):,} Kč

Pod trhem: {int(discount)} %

{link}

-------------------
"""
    )
if results:
    body = "\n".join(results)

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
