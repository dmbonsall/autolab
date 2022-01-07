from functools import lru_cache
import logging
import logging.config
from pathlib import Path

from pydantic import BaseSettings


class AnsibleConfiguration(BaseSettings):
    create_vm_private_data_dir: Path = "../../ansible-projects/pve-one-touch"
    create_vm_playbook: str = "create-vm.yml"
    ip_print_task_name: str = "Print the IPv4 addresses on all interfaces"
    config_backup_private_data_dir: Path = "../../ansible-projects/config-backup"
    config_backup_playbook: str = "config-backup.yml"


@lru_cache
def get_ansible_configuration():
    return AnsibleConfiguration()

# Copied from uvicorn
TRACE_LOG_LEVEL: int = 5
LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(module)s %(message)s",
            "use_colors": None,
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "autolab": {"handlers": ["default"], "level": "DEBUG"},
    }
}


logging.addLevelName(TRACE_LOG_LEVEL, "TRACE")
logging.config.dictConfig(LOGGING_CONFIG)

@lru_cache
def get_logger():
    return  logging.getLogger("autolab")
