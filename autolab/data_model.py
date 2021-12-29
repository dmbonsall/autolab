from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseModel, BaseSettings


class VmTemplateType(Enum):
    ALMA = "AlmaCloudInit"
    UBUNTU = "UbuntuCloudInit"


class AnsibleRunnerStatus(Enum):
    STARTING = "starting"
    RUNNING = "running"
    SUCCESSFUL = "successful"
    TIMEOUT = "timeout"
    FAILED = "failed"
    CANCELED = "canceled"


class BaseRequest(BaseModel):
    """Base class for REST request data."""


class BaseResponse(BaseModel):
    """Base class for REST response data."""
    status: AnsibleRunnerStatus


class CreateVmRequest(BaseRequest):
    vm_name: str
    vm_template: VmTemplateType


class CreateVmResponse(BaseResponse):
    ip_addrs: List[str]
    request: CreateVmRequest

class ConfigBackupRequest(BaseRequest):
    pass

class ConfigBackupResponse(BaseResponse):
    pass

class AnsibleConfiguration(BaseSettings):
    create_vm_private_data_dir: Path = "ansible/pve-one-touch"
    create_vm_playbook: str = "create-vm.yml"
    ip_print_task_name: str = "Print the IPv4 addresses on all interfaces"
    config_backup_private_data_dir: Path = "ansible/config-backup"
    config_backup_playbook: str = "config-playbook.yml"


@lru_cache
def get_ansible_configuration():
    return AnsibleConfiguration()
