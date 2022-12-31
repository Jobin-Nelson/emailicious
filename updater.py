#!/usr/bin/env python3
'''This script sends email updates''' 
from __future__ import annotations
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from email.message import EmailMessage
import smtplib, ssl, os, base64

load_dotenv()

email_sender = os.getenv('EMAIL_SENDER')
email_password = os.getenv('EMAIL_PASSWORD')
email_receiver = os.getenv('EMAIL_RECEIVER')

today = datetime.today()

daily_update_path = Path.home() / 'playground' / 'dev' / 'illumina' / 'daily_updates' / f'{today:%Y-%m-%d}.txt'

def main() -> int:
    if not is_env_set():
        print('Environment variables are not set properly')
        return 1

    email_to_sent = gen_email()

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, base64.b64decode(email_password).decode().strip())
        smtp.sendmail(email_sender, email_receiver, email_to_sent.as_string())
        print(f'Daily email update send for {today:%Y-%m-%d}')

    return 0

def is_env_set() -> bool:
    return all(e for e in [email_sender, email_password, email_receiver])

def gen_email() -> EmailMessage:
    subject = 'Daily update'
    body = ''
    if daily_update_path.exists():
        body = daily_update_path.read_text()

    body = body or 'No updates for today'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)
    return em

if __name__ == '__main__':
    raise SystemExit(main())
