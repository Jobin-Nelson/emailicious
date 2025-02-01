
from email.message import EmailMessage
from pathlib import Path
import smtplib, ssl

from emailicious.utils import bail, ExitCode
from emailicious.config import Config


def gmail_main() -> int:
    config = Config()

    email_to_sent = _gen_gmail(config)
    _send_gmail(config, email_to_sent)
    return 0

def _gen_gmail(config: Config) -> EmailMessage:
    '''Generates today's email'''
    subject = 'Daily update'
    gmail_config = config.config['gmail']

    em = EmailMessage()
    em['From'] = gmail_config['email_sender']
    em['To'] = gmail_config['email_receiver']
    em['Subject'] = subject
    em.set_content(_get_body(config.daily_update_path))
    return em


def _get_body(body_path: Path) -> str:
    '''Returns the file contents for today'''
    if body_path.exists():
        return body_path.read_text()
    else:
        return 'No updates for today\n'


def _send_gmail(config: Config, email_to_sent: EmailMessage) -> None:
    '''Sends the email'''
    context = ssl.create_default_context()
    gmail_config = config.config['gmail']

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(
                gmail_config['email_sender'],
                gmail_config['email_password'],
            )
            smtp.sendmail(
                gmail_config['email_sender'],
                gmail_config['email_receiver'],
                email_to_sent.as_string(),
            )
    except smtplib.SMTPException as e:
        bail(
            f'Could not send email, encountered an exception {e}',
            ExitCode.EMAIL_NOT_SEND,
        )
    else:
        print(f'Daily email update send for {config.today:%Y-%m-%d}')
