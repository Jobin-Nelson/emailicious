'''This module tests the updater'''
from email.message import EmailMessage
import urllib.request
import updater
import pytest
import importlib

def setup_function():
    importlib.reload(updater)

def has_connection() -> bool:
    url = 'http://google.com'
    try:
        urllib.request.urlopen(url, timeout=3)
    except Exception:
        return False
    return True

def test_env_is_empty():
    updater.EMAIL_SENDER = ''
    assert updater.is_env_set() == False

def test_env_not_found():
    updater.EMAIL_SENDER = None
    assert updater.is_env_set() == False

def test_env_all_set():
    updater.EMAIL_SENDER = 'sender@gmail.com'
    updater.EMAIL_PASSWORD = 'senderpass$'
    updater.EMAIL_RECEIVER = 'receiver@gmail.com'
    assert updater.is_env_set()

def test_email_body_if_path_not_exist(tmp_path):
    updater.DAILY_UPDATE_PATH = tmp_path / 'non-existing-dir' / 'non-existing-file.txt'
    assert updater.get_body() is None

def test_email_body_if_path_exist(tmp_path):
    tmp_file = tmp_path / 'test.txt'
    body = 'Testing get_body() function\n'
    tmp_file.write_text(body)
    updater.DAILY_UPDATE_PATH = tmp_file
    assert updater.get_body() == body

def test_gen_email():
    assert isinstance(updater.gen_email(), EmailMessage)

def test_gen_email_body_if_content_exist(tmp_path):
    tmp_file = tmp_path / 'test.txt'
    body = 'Testing get_body() function\n'
    tmp_file.write_text(body)
    updater.DAILY_UPDATE_PATH = tmp_file
    em = updater.gen_email()
    assert em.get_content() == body


def test_gen_email_body_if_content_empty(tmp_path):
    tmp_file = tmp_path / 'test.txt'
    body = ''
    tmp_file.write_text(body)
    updater.DAILY_UPDATE_PATH = tmp_file
    em = updater.gen_email()
    assert em.get_content() == updater.PLACEHOLDER_BODY

@pytest.mark.skipif(not has_connection(), reason='No internet connection')
def test_send_email(tmp_path, capsys):
    tmp_file = tmp_path / 'test.txt'
    body = 'Testing send_email() function\n'
    tmp_file.write_text(body)

    updater.EMAIL_RECEIVER = updater.EMAIL_SENDER

    updater.DAILY_UPDATE_PATH = tmp_file

    updater.send_email(updater.gen_email())
    stdout, _ = capsys.readouterr()
    assert stdout == f'Daily email update send for {updater.TODAY:%Y-%m-%d}\n'
