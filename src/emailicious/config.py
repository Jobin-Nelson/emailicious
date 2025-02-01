import configparser
from datetime import datetime
from pathlib import Path

from emailicious.utils import bail, ExitCode

class Config:
    config_path = Path.home() / '.config' / 'emailicious' / 'config.ini'
    today = datetime.today()
    _config_template_path = Path(__file__).parent / 'config_template.ini'

    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self._read_config()
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
