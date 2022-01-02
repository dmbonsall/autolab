from functools import lru_cache
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
