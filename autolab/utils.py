import datetime

import ansible_runner

from autolab import database
from autolab.schema import AnsibleRunnerStatus, StatusHandlerStatus


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
        raise RuntimeError("Unable to find ip address of the new VM")

    if len(ip_print_events) > 1:
        raise RuntimeError("Too many ip print events found")

    # ===== Grab the ip addresses and return the response =====
    ip_addrs = ip_print_events[0]["event_data"]["res"]["msg"]
    database.update_ansible_job(runner.config.ident, result=ip_addrs)


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
