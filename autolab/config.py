from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseSettings

from autolab import schema, utils

_DEFAULT_CONFIG_PATH = "/etc/autolab.json"


@lru_cache
def get_config_file_name() -> Path:
    path_str = os.environ.get("AUTOLAB_CONFIG", _DEFAULT_CONFIG_PATH)
    return Path(path_str)


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    return json.loads(Path(get_config_file_name()).read_text(encoding))


class ApplicationSettings(BaseSettings):
    db_url: str = "sqlite:///sql_app.db"
    max_executor_threads: int = 1
    create_vm_private_data_dir: str = "./ansible/pve-one-touch"
    config_backup_private_data_dir: str = "./ansible/config-backup"
    ansible_quiet: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                json_config_settings_source,
                file_secret_settings,
            )


_settings = ApplicationSettings()

def get_app_settings():
    return _settings


_playbook_configs = {
    schema.PlaybookType.CREATE_VM: schema.PlaybookConfig(
        private_data_dir=_settings.create_vm_private_data_dir,
        playbook="create-vm.yml",
        quiet=_settings.ansible_quiet,
        finished_callback=utils.get_ip_addrs,
    ),

    schema.PlaybookType.CONFIG_BACKUP: schema.PlaybookConfig(
        private_data_dir=_settings.config_backup_private_data_dir,
        playbook="config-backup.yml",
        quiet=_settings.ansible_quiet,
    )
}

def get_playbook_config(playbook_type: schema.PlaybookType):
    return _playbook_configs[playbook_type]
