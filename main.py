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

    seo = item.get("seo", {})
    category = seo.get("category_main_cb", "byt")
    locality = seo.get("locality", "praha")

    hash_id = item.get("hash_id", "")

    link = f"https://www.sreality.cz/detail/prodej/{category}/{locality}/{hash_id}"

    results.append(
        f"{name} - {price} Kč\n{link}\n"
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
