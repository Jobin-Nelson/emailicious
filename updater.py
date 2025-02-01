#!/usr/bin/env python3
'''This module sends email updates'''

from __future__ import annotations
from enum import IntEnum
from datetime import datetime
from pathlib import Path
from email.message import EmailMessage
import smtplib, ssl, os, base64, sys, configparser
from typing import NoReturn


class ExitCode(IntEnum):
    CONFIG_NOT_FOUND = 1
    EMAIL_NOT_SEND = 2


def bail(message: str, code: ExitCode) -> NoReturn:
    '''Prints a message and exits with a code'''
    print(message, file=sys.stderr)
    sys.exit(code.value)


class Config:
    config_path = Path.home() / '.config' / 'mailinator' / 'config.ini'
    today = datetime.today()
    _config_template_path = Path(__file__).parent / 'config_template.ini'

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self._read_config()
        print(vars(self.config))
        self.daily_update_path = (
            Path(self.config['data']['daily_update_dir']).expanduser().resolve()
            / f'{Config.today:%Y-%m-%d}.md'
        )

    def _read_config(self) -> None:
        if not self.config.read(self.config_path):
            if self.config_path.exists():
                self.config_path.rename(self.config_path.with_suffix('.bak'))
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as file:
                config_template = configparser.ConfigParser()
                config_template.read(Config._config_template_path)
                config_template.write(file)
            bail(
                f'Config file not found at {self.config_path}.\n'
                'Auto generating the config file.\n'
                'Please fill out the config file before executing again.\n',
                ExitCode.CONFIG_NOT_FOUND,
            )


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


def send_gmail(config: Config, email_to_sent: EmailMessage) -> None:
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
