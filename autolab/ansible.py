from concurrent.futures import Executor, Future
import datetime
from typing import Any, Callable, Dict, Optional

import ansible_runner
import ansible_runner.interface
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from . import database
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
    database.update_ansible_job(runner.config.ident, result=ip_addrs)

class PlaybookConfig(BaseModel):
    private_data_dir: str
    playbook: str
    quiet: bool = True
    finished_callback: Optional[Callable[[ansible_runner.Runner], None]] = None

    class Config:
        allow_mutation = False


def status_handler(status: StatusHandlerStatus, runner_config: ansible_runner.RunnerConfig):
    """Callback to handle changes to status."""
    status = StatusHandlerStatus(**status)
    cur_time = datetime.datetime.now()
    if status.status == AnsibleRunnerStatus.STARTING:
        database.update_ansible_job(runner_config.ident, start_time=cur_time, status=status.status)
    elif status.status == AnsibleRunnerStatus.RUNNING:
        database.update_ansible_job(runner_config.ident, status=status.status)
    else:
        # We have reached a terminal state
        database.update_ansible_job(runner_config.ident, status=status.status, end_time=cur_time)


class AnsibleJobExecutorService:
    def __init__(self,
                 executor: Executor,
                 status_handler: Callable[[StatusHandlerStatus, ansible_runner.interface.RunnerConfig], None]):
        self._executor: Executor = executor
        self._status_handler = status_handler
        self._future_map = {}

    def submit_job(self, ident: str, config: PlaybookConfig, extravars: Optional[dict] = None):
        if extravars is None:
            extravars = {}

        future = self._executor.submit(ansible_runner.run,
                                       status_handler = self._status_handler,
                                       ident=ident,
                                       extravars=extravars,
                                       **config.dict())

        future.add_done_callback(self.done_callback)
        self._future_map[ident] = future
        logger.info("Submitted job: %s", ident)

    def done_callback(self, future: Future):
        runner: ansible_runner.Runner = future.result()
        self._future_map.pop(runner.config.ident)
        logger.info("Finished job: %s", runner.config.ident)
