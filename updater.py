#!/usr/bin/env python3
'''This script sends email updates''' 
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from email.message import EmailMessage
import smtplib, ssl, os

load_dotenv()

email_sender = os.getenv('EMAIL_SENDER')
email_password = os.getenv('EMAIL_PASSWORD')
email_receiver = os.getenv('EMAIL_RECEIVER')

today = datetime.today()

daily_update_path = Path.home() / 'playground' / 'dev' / 'illumina' / 'daily_updates' / f'{today:%Y-%m-%d}.txt'

def main() -> int:
    subject = 'Daily update'
    if daily_update_path.exists():
        body = daily_update_path.read_text()
    else:
        body = 'No updates for today'

    if not email_password:
        print('No email password is found')
        return 1

    if not email_receiver:
        print('No email receiver is found')
        return 1

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

    print(f'Daily email update send for {today:%Y-%m-%d}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
