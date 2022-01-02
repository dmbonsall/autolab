from abc import ABC, abstractmethod
import asyncio
import datetime
from threading import Thread
from typing import Optional
import uuid

import ansible_runner
from sqlalchemy.orm import Session

from . import crud
from .schema import (BaseRequest, BaseResponse, ConfigBackupResponse, CreateVmRequest, CreateVmResponse,
                     AnsibleRunnerStatus)
from .config import AnsibleConfiguration


async def await_thread(thread: Thread):
    """Block until a thread has terminated, but perform sleep operations with ``asyncio.sleep``."""
    while thread.is_alive():
        await asyncio.sleep(1)


def task_result_event_filter(event: dict, task_name: str) -> bool:
    """Filter to find the ``runner_on_ok`` event for a given task name."""
    try:
        return event["event_data"]["task"] == task_name and \
                event["event"] == "runner_on_ok"
    except KeyError:
        return False


class AnsibleExecutor(ABC):
    """Base class for executors of ansible playbooks.

    Provides an abstraction layer on top of ansible-runner.
    """
    def __init__(self, config: AnsibleConfiguration) -> None:
        self.config = config

    def pre_exec(self, db: Session) -> str:
        start_time = datetime.datetime.now()
        job_uuid = str(uuid.uuid1())
        crud.create_ansible_job(db, job_uuid, start_time)
        return job_uuid

    def post_exec(self, db: Session, job_uuid: str, status: AnsibleRunnerStatus):
        end_time = datetime.datetime.now()
        crud.update_ansible_job_status(db, job_uuid, status, end_time)

    @abstractmethod
    async def execute(self, db: Session, request: Optional[BaseRequest]) -> BaseResponse:
        """Executes the ansible playbook."""


class CreateVMExecutor(AnsibleExecutor):
    """Executor to run the create-vm playbook to create a virtual machine."""
    async def execute(self, db: Session, request: CreateVmRequest) -> CreateVmResponse:
        """Executes the ansible playbook."""
        # ===== Run the ansible playbook asyncronously and wait for the thread to complete =====
        job_uuid = self.pre_exec(db)
        extravars = {"vm_name": request.vm_name, "template_name": request.vm_template.value}
        thread, runner = ansible_runner.run_async(private_data_dir=self.config.create_vm_private_data_dir,
                                                  playbook=self.config.create_vm_playbook,
                                                  extravars=extravars,
                                                  ident=job_uuid,
                                                  quiet=True)

        await await_thread(thread)

        # ===== Assert that the status is successful =====
        status = AnsibleRunnerStatus(runner.status)
        self.post_exec(db, job_uuid, status)
        if status != AnsibleRunnerStatus.SUCCESSFUL:
            raise RuntimeError("Ansible run job for create-vm failed")

        # ===== Find the ip print task from the events list =====
        ip_print_events = [e for e in runner.events if task_result_event_filter(e, self.config.ip_print_task_name)]

        if not ip_print_events:
            raise RuntimeError("Unable to find ip address of the new VM")

        if len(ip_print_events) > 1:
            raise RuntimeError("Too many ip print events found")

        # ===== Grab the ip addresses and return the response =====
        ip_addrs = ip_print_events[0]["event_data"]["res"]["msg"]
        return CreateVmResponse(job_uuid=job_uuid, status=status, ip_addrs=ip_addrs, request=request)


class ConfigBackupExecutor(AnsibleExecutor):
    """Executor to run the create-vm playbook to create a virtual machine."""
    async def execute(self, db: Session, _ = None) -> ConfigBackupResponse:
        """Executes the ansible playbook."""
        # ===== Run the ansible playbook asyncronously and wait for the thread to complete =====
        job_uuid = self.pre_exec(db)
        thread, runner = ansible_runner.run_async(private_data_dir=self.config.config_backup_private_data_dir,
                                                  playbook=self.config.config_backup_playbook,
                                                  quiet=False)


        await await_thread(thread)

        # ===== Assert that the status is successful =====
        status = AnsibleRunnerStatus(runner.status)
        self.post_exec(db, job_uuid, status)
        if status != AnsibleRunnerStatus.SUCCESSFUL:
            raise RuntimeError("Ansible run job for config-backup failed")

        return ConfigBackupResponse(job_uuid=job_uuid, status=status)
