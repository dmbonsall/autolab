import asyncio
import datetime
from threading import Thread
from typing import Any, Callable, Dict, Optional
import uuid

import ansible_runner
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from . import crud
from .schema import AnsibleRunnerStatus, StatusHandlerStatus
from .config import get_logger


logger = get_logger()


def task_result_event_filter(event: dict, task_name: str) -> bool:
    """Filter to find the ``runner_on_ok`` event for a given task name."""
    try:
        return event["event_data"]["task"] == task_name and \
                event["event"] == "runner_on_ok"
    except KeyError:
        return False

def get_ip_addrs(runner: ansible_runner.Runner):
    status = AnsibleRunnerStatus(runner.status)
    if status != AnsibleRunnerStatus.SUCCESSFUL:
        return

    # ===== Find the ip print task from the events list =====
    ip_print_events = [e for e in runner.events if task_result_event_filter(e, "Print the IPv4 addresses on all interfaces")]

    if not ip_print_events:
        logger.error("Unable to find ip address of the new VM")
        return

    if len(ip_print_events) > 1:
        logger.error("Too many ip print events found")
        return

    # ===== Grab the ip addresses and return the response =====
    ip_addrs = ip_print_events[0]["event_data"]["res"]["msg"]
    crud.update_job(runner.config.ident, result=ip_addrs)

class PlaybookConfig(BaseModel):
    private_data_dir: str
    playbook: str
    quiet: bool = True
    finished_callback: Optional[Callable[[ansible_runner.Runner], None]] = None

    class Config:
        allow_mutation = False


class PlaybookExecutor:
    def __init__(self, config: PlaybookConfig):
        self._uuid: str = str(uuid.uuid1())
        self._config: PlaybookConfig = config
        self._start_time: Optional[datetime.datetime] = None
        self._end_time: Optional[datetime.datetime] = None
        self._runner: Optional[ansible_runner.Runner] = None
        self._runner_thread: Optional[Thread] = None

    config = property(lambda self: self._config)
    uuid = property(lambda self: self._uuid)

    def start_playbook(self, extravars: Optional[Dict[str, str]] = None):
        if extravars is None:
            extravars = {}

        self._start_time = datetime.datetime.now()
        thread, runner = ansible_runner.run_async(ident=self._uuid,
                                                  status_handler=self.status_handler,
                                                  extravars=extravars,
                                                  **self.config.dict())
        self._runner_thread = thread
        self._runner = runner

    async def await_termination(self):
        """Block until a thread has terminated, but perform sleep operations with ``asyncio.sleep``."""
        while self._runner_thread.is_alive():
            await asyncio.sleep(1)


    def status_handler(self, status: StatusHandlerStatus, _: Optional[Any] = None):
        """Callback to handle changes to status."""
        # NOTE: _ is the runner config, it is not needed since we can access via self.runner.config
        status = StatusHandlerStatus(**status)
        if status.status == AnsibleRunnerStatus.STARTING:
            crud.create_ansible_job(self.uuid, self._start_time)
            crud.update_job(self.uuid, status=status.status)
        elif status.status == AnsibleRunnerStatus.RUNNING:
            crud.update_job(self.uuid, status=status.status)
        else:
            # We have reached a terminal state
            self._end_time = datetime.datetime.now()
            crud.update_job(self.uuid, status=status.status, end_time=self._end_time)


class PlaybookExecutorFactory:
    def __init__(self):
        self._config_map = {}

    def register(self, key, config: PlaybookConfig):
        self._config_map[key] = config

    def build_executor(self, key):
        return PlaybookExecutor(self._config_map[key])
