import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import re

SEARCH_URL = "https://www.sreality.cz/hledani/prodej/byty"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(SEARCH_URL, headers=headers)

html = r.text

soup = BeautifulSoup(html, "html.parser")

results = []

cards = soup.find_all("a")

for card in cards:

    href = card.get("href", "")

    if "/detail/prodej/byt/" not in href:
        continue

    title = card.get_text(" ", strip=True)

    if len(title) < 10:
        continue

    full_link = "https://www.sreality.cz" + href

    # zkusí vytáhnout cenu
    price_match = re.search(r'(\d[\d\s]+)\s*Kč', title)

    price_text = price_match.group(1) if price_match else "?"

    results.append(
        f"""
{title}

Cena: {price_text} Kč

{full_link}

----------------------------------------
"""
    )

# odstranění duplicit
results = list(dict.fromkeys(results))

body = "\n".join(results[:20])

if not body:
    body = "Žádné výsledky."

msg = MIMEText(body)

msg["Subject"] = "Sreality REAL alert"
msg["From"] = os.environ["SMTP_USER"]
msg["To"] = os.environ["EMAIL_TO"]

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(
    os.environ["SMTP_USER"],
    os.environ["SMTP_PASSWORD"]
)

server.send_message(msg)

server.quit()
