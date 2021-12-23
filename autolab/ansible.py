from abc import ABC, abstractmethod
import asyncio
from threading import Thread

import ansible_runner

from .data_model import (BaseRequest, BaseResponse, CreateVmRequest, CreateVmResponse,
                         AnsibleConfiguration, AnsibleRunnerStatus)


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

    @abstractmethod
    async def execute(self, request: BaseRequest) -> BaseResponse:
        """Executes the ansible playbook."""


class CreateVMExecutor(AnsibleExecutor):
    """Executor to run the create-vm playbook to create a virtual machine."""
    async def execute(self, request: CreateVmRequest) -> CreateVmResponse:
        """Executes the ansible playbook."""
        # ===== Run the ansible playbook asyncronously and wait for the thread to complete =====
        extravars = {"vm_name": request.vm_name, "template_name": request.vm_template.value}
        thread, runner = ansible_runner.run_async(private_data_dir=self.config.create_vm_private_data_dir,
                                                  playbook=self.config.create_vm_playbook,
                                                  extravars=extravars,
                                                  quiet=True)

        await await_thread(thread)

        # ===== Assert that the status is successful =====
        status = AnsibleRunnerStatus(runner.status)
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
        return CreateVmResponse(status=status, ip_addrs=ip_addrs, request=request)
