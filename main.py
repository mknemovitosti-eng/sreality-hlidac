import requests
import smtplib
from email.mime.text import MIMEText
import os
import json

URL = "https://www.sreality.cz/api/cs/v2/estates"

params = {
    "category_main_cb": 1,
    "category_type_cb": 1,
    "per_page": 5
}

r = requests.get(URL, params=params)

data = r.json()

body = json.dumps(data, indent=2, ensure_ascii=False)[:15000]

msg = MIMEText(body)

msg["Subject"] = "DEBUG Sreality"
msg["From"] = os.environ["SMTP_USER"]
msg["To"] = os.environ["EMAIL_TO"]

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

server.login(
    os.environ["SMTP_USER"],
    os.environ["SMTP_PASSWORD"]
)

server.send_message(msg)

server.quit()
