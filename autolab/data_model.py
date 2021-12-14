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


class CreateVmRequest(BaseRequest):
    vm_name: str
    vm_template: VmTemplateType


class CreateVmResponse(BaseResponse):
    status: AnsibleRunnerStatus
    ip_addrs: List[str]
    request: CreateVmRequest


class AnsibleConfiguration(BaseSettings):
    private_data_dir: Path = "ansible"
    create_vm_playbook: str = "create-vm.yml"
    ip_print_task_name: str = "Print the IPv4 addresses on all interfaces"


@lru_cache
def get_ansible_configuration():
    return AnsibleConfiguration()
