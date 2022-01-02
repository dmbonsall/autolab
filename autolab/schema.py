import datetime
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .data_model import AnsibleRunnerStatus, VmTemplateType


class AnsibleJob(BaseModel):
    job_uuid: str
    status: AnsibleRunnerStatus
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


class BaseRequest(BaseModel):
    """Base class for REST request data."""


class BaseResponse(BaseModel):
    """Base class for REST response data."""
    job_uuid: str
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
