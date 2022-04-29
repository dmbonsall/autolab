import enum
import datetime
from typing import Any, Callable, Dict, List, Optional

import ansible_runner
from pydantic import BaseModel  # pylint: disable=no-name-in-module


class PlaybookType(enum.Enum):
    CREATE_VM = "create-vm"
    CONFIG_BACKUP = "config-backup"


class PlaybookConfig(BaseModel):
    private_data_dir: str
    artifact_dir: str
    playbook: str
    quiet: bool = True
    finished_callback: Optional[Callable[[ansible_runner.Runner], None]] = None

    class Config:
        allow_mutation = False


class AnsibleRunnerStatus(enum.Enum):
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    SUCCESSFUL = "successful"
    TIMEOUT = "timeout"
    FAILED = "failed"
    CANCELED = "canceled"


class VmTemplateType(enum.Enum):
    ALMA = "AlmaCloudInit"
    UBUNTU = "UbuntuCloudInit"


class AnsibleJob(BaseModel):
    job_uuid: str
    status: AnsibleRunnerStatus
    start_time: Optional[datetime.datetime]
    end_time: Optional[datetime.datetime] = None
    result: Optional[Any] = None

    class Config:
        orm_mode = True

class StatusHandlerStatus(BaseModel):
    """The status structure that is passed back from the ansible_runner.Runner class to status handler."""
    status: AnsibleRunnerStatus
    runner_ident: str


class BaseRequest(BaseModel):
    """Base class for REST request data."""


class BaseResponse(BaseModel):
    """Base class for REST response data."""
    job_uuid: str

class StartPlaybookRequest(BaseModel):
    """Request model for starting a playbook."""
    extravars: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


StatusHandlerInterface = Callable[[StatusHandlerStatus, ansible_runner.interface.RunnerConfig], None]
