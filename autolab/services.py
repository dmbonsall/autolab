from concurrent.futures import Executor, Future
import logging
from typing import Optional

import ansible_runner
import ansible_runner.interface

from autolab import config
from autolab.schema import PlaybookType, StatusHandlerInterface


logger = logging.getLogger("autolab")


class PlaybookExecutorService:
    def __init__(self, executor: Executor, status_handler: StatusHandlerInterface):
        self._executor: Executor = executor
        self._status_handler = status_handler
        self._future_map = {}

    def submit_job(self, ident: str, playbook_type: PlaybookType, extravars: Optional[dict] = None):
        if extravars is None:
            extravars = {}

        playbook_config = config.get_playbook_config(playbook_type)

        future = self._executor.submit(ansible_runner.run,
                                       status_handler = self._status_handler,
                                       ident=ident,
                                       extravars=extravars,
                                       **playbook_config.dict())

        future.add_done_callback(self.done_callback)
        self._future_map[ident] = future
        logger.info("Submitted job: %s", ident)

    def done_callback(self, future: Future):
        runner: ansible_runner.Runner = future.result()
        self._future_map.pop(runner.config.ident)
        logger.info("Finished job: %s", runner.config.ident)
