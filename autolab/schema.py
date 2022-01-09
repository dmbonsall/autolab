import datetime
from typing import Any, Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from .data_model import AnsibleRunnerStatus, VmTemplateType


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


class CreateVmRequest(BaseRequest):
    vm_name: str
    vm_template: VmTemplateType
