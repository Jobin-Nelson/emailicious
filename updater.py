#!/usr/bin/env python3
'''This script sends email updates''' 
from __future__ import annotations
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from email.message import EmailMessage
import smtplib, ssl, os, base64, sys

load_dotenv()

EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')

TODAY = datetime.today()

DAILY_UPDATE_PATH = Path.home() / 'playground' / 'dev' / 'illumina' / 'daily_updates' / f'{TODAY:%Y-%m-%d}.txt'

PLACEHOLDER_BODY = 'No updates for today\n'

def main() -> int:
    '''Sends an email update for today'''
    if not is_env_set():
        print('Environment variables are not set properly', file=sys.stderr)
        return 1

    email_to_sent = gen_email()

    send_email(email_to_sent)

    return 0

def is_env_set() -> bool:
    '''Checks if required environment variables are set'''
    return all(e for e in [EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER])

def gen_email() -> EmailMessage:
    '''Generates today's email'''
    subject = 'Daily update'

    body = get_body() or PLACEHOLDER_BODY

    em = EmailMessage()
    em['From'] = EMAIL_SENDER
    em['To'] = EMAIL_RECEIVER
    em['Subject'] = subject
    em.set_content(body)
    return em

def get_body() -> str | None:
    '''Returns the file contents for today'''
    if DAILY_UPDATE_PATH.exists():
        return DAILY_UPDATE_PATH.read_text()

def send_email(email_to_sent: EmailMessage) -> None:
    '''Sends the email'''
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(EMAIL_SENDER, base64.b64decode(EMAIL_PASSWORD).decode().strip())
            smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, email_to_sent.as_string())
    except smtplib.SMTPException as e:
        print(f'Could not send email, encountered an exception {e}', file=sys.stderr)
        sys.exit(1)
    else:
        print(f'Daily email update send for {TODAY:%Y-%m-%d}')

if __name__ == '__main__':
    raise SystemExit(main())
