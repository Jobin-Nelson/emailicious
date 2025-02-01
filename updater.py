#!/usr/bin/env python3
'''This module sends email updates'''

from __future__ import annotations
from enum import IntEnum
from datetime import datetime
from pathlib import Path
from email.message import EmailMessage
import smtplib, ssl, os, base64, sys, tomllib
from typing import Any, NoReturn


class ExitCode(IntEnum):
    CONFIG_NOT_FOUND = 1
    EMAIL_NOT_SEND = 2


def bail(message: str, code: ExitCode) -> NoReturn:
    '''Prints a message and exits with a code'''
    print(message, file=sys.stderr)
    sys.exit(code.value)


class Config:
    def __init__(self) -> None:
        self.config_path = Path.home() / '.config' / 'mailinator' / 'config.toml'
        self.config = self._read_config()

        self.email_sender = self.config.get('email_sender', '')
        self.email_password = self.config.get('email_password', '')
        self.email_receiver = self.config.get('email_receiver', '')
        self.daily_update_dir = self.config.get('daily_update_dir', '')

        self._validate()
        self.today = datetime.today()
        self.daily_update_path = (
            Path(self.daily_update_dir).expanduser().resolve()
            / f'{self.today:%Y-%m-%d}.md'
        )

    def _read_config(self) -> dict[str, Any]:
        try:
            with open(self.config_path, 'rb') as file:
                return tomllib.load(file)
        except Exception:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as file:
                file.write(
                    'email_sender = ""\n'
                    'email_password = ""\n'
                    'email_receiver = ""\n'
                    'daily_update_dir = ""\n'
                )
            bail(
                f'Config file not found at {self.config_path}.\n'
                'Auto generating the config file.\n'
                'Please fill out the config file before executing again.\n',
                ExitCode.CONFIG_NOT_FOUND,
            )

    def _validate(self) -> None:
        '''Checks if required environment variables are set'''
        missing_configs = [
            e
            for e in [
                self.email_sender,
                self.email_password,
                self.email_receiver,
                self.daily_update_dir,
            ]
            if not e
        ]
        if missing_configs:
            print(f'ERROR: Missing config fields {missing_configs}', file=sys.stderr)
            sys.exit(ExitCode.CONFIG_NOT_FOUND)


def main() -> int:
    '''Sends an email update for today'''
    config = Config()

    # email_to_sent = gen_email(config)
    # send_email(config, email_to_sent)
    return 0


def gen_email(config: Config) -> EmailMessage:
    '''Generates today's email'''
    subject = 'Daily update'

    em = EmailMessage()
    em['From'] = config.email_sender
    em['To'] = config.email_receiver
    em['Subject'] = subject
    em.set_content(get_body(config))
    return em


def get_body(config: Config) -> str:
    '''Returns the file contents for today'''
    if config.daily_update_path.exists():
        return config.daily_update_path.read_text()
    else:
        return 'No updates for today\n'


def send_email(config: Config, email_to_sent: EmailMessage) -> None:
    '''Sends the email'''
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(
                config.email_sender,
                base64.b64decode(config.email_password).decode().strip(),
            )
            smtp.sendmail(
                config.email_sender, config.email_receiver, email_to_sent.as_string()
            )
    except smtplib.SMTPException as e:
        print(f'Could not send email, encountered an exception {e}', file=sys.stderr)
        sys.exit(ExitCode.EMAIL_NOT_SEND)
    else:
        print(f'Daily email update send for {config.today:%Y-%m-%d}')


if __name__ == '__main__':
    raise SystemExit(main())
