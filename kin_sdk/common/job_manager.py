"""
Job Management System

This module provides a job management system with support for asynchronous job execution,
status tracking, and output streaming.
"""

import uuid
import threading
from collections import UserDict
from queue import Queue
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Iterator
from concurrent.futures import Future, ThreadPoolExecutor

from pydantic import BaseModel, ConfigDict, Field

from kin_sdk.agent_module._module.base import BaseModule


class ConcurrentDict(UserDict):
    """TODO: sphinx docstring"""

    def __init__(self, *args, **kwargs):
        self.lock = threading.RLock()  # Using RLock instead of Lock
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        if self.lock.acquire(timeout=5):  # 5 seconds timeout
            try:
                return super().__getitem__(key)
            finally:
                self.lock.release()
        else:
            raise RuntimeError("Lock acquisition timed out in __getitem__")

    def __setitem__(self, key, value):
        if self.lock.acquire(timeout=5):  # 5 seconds timeout
            try:
                return super().__setitem__(key, value)
            finally:
                self.lock.release()
        else:
            raise RuntimeError("Lock acquisition timed out in __setitem__")

    def __delitem__(self, key):
        if self.lock.acquire(timeout=5):  # 5 seconds timeout
            try:
                return super().__delitem__(key)
            finally:
                self.lock.release()
        else:
            raise RuntimeError("Lock acquisition timed out in __delitem__")

    def get(self, key, default=None):
        if self.lock.acquire(timeout=5):  # 5 seconds timeout
            try:
                return super().get(key, default)
            finally:
                self.lock.release()
        else:
            raise RuntimeError("Lock acquisition timed out in get")


class JobStatus(Enum):
    """
    Enumeration of possible job statuses.
    """

    STARTING = 0
    PROCESSING = 1
    CANCELED = 2
    FAILED = 3
    EXPIRED = 4
    SUCCESS = 5
    STOPPED = 6


class Job(BaseModel):
    """
    Represents a job with its associated data and methods.

    :param input_data: The input data for the job.
    :param setup_id: The setup ID associated with the job.
    :param module_ids: List of module IDs associated with the job.
    :param status: The current status of the job.
    :param task: The Future object representing the job's task.
    :param outputs: A queue to store job outputs.
    :param stop_event: An event to signal job termination.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    module: BaseModule = Field(..., description="The module associated with the job")
    input_data: BaseModel = Field(..., description="The input data for the job")
    setup_id: str = Field(..., description="The setup ID for the job")
    module_ids: List[str] = Field(
        [], description="List of module IDs associated with the job"
    )
    status: JobStatus = Field(
        JobStatus.STARTING, description="The current status of the job"
    )
    task: Future = Field(default_factory=Future)
    outputs: Queue = Field(default_factory=Queue)
    stop_event: threading.Event = Field(default_factory=threading.Event)

    def add_to_outputs(self, item: Any) -> None:
        """
        Adds an item to the job's output queue.

        :param item: The item to be added to the outputs.
        """
        self.outputs.put(item)  # pylint: disable=no-member

    def stop_outputs(self) -> None:
        """
        Signals the termination of the job's output stream.
        """
        self.stop_event.set()  # pylint: disable=no-member
        self.outputs.put(None)  # pylint: disable=no-member # Sentinel value

    def get_outputs(self) -> Iterator[Any]:
        """
        Returns an iterator for the job's output items.

        :return: An iterator yielding output items.
        """
        while not self.stop_event.is_set():  # pylint: disable=no-member
            item = self.outputs.get()  # pylint: disable=no-member
            if item is None:  # Check for sentinel value
                break
            yield item


class JobManager:
    """
    Manages the lifecycle of jobs, including creation, retrieval, and termination.

    :param max_workers: The maximum number of worker threads for job execution.
    """

    def __init__(self, max_workers: int = 10):
        self.jobs: Dict[str, Job] = ConcurrentDict()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()

    def start_job(
        self,
        module: BaseModule,
        input_data: BaseModel,
        setup_id: str,
        module_ids: List[str],
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """
        Creates and starts a new job with the given parameters.

        :param input_data: The input data for the job.
        :param setup_id: The setup ID for the job.
        :param module_ids: List of module IDs associated with the job.
        :param func: The function to be executed as the job.
        :param args: Positional arguments for the job function.
        :param kwargs: Keyword arguments for the job function.
        :return: The ID of the newly created job.
        """
        job_id = f"jobs:{uuid.uuid4().hex}"
        start_event = threading.Event()

        def wrapped_func():
            start_event.wait()  # Attendre que le job soit stocké
            return func(job_id, *args, **kwargs)

        try:
            job = Job(
                module=module,
                input_data=input_data,
                setup_id=setup_id,
                module_ids=module_ids,
                status=JobStatus.STARTING,
                task=self.executor.submit(wrapped_func),
                outputs=Queue(),
                stop_event=threading.Event(),
            )
            self.jobs[job_id] = job
            start_event.set()  # Signaler que le job est stocké
            return job_id
        except Exception as e:
            raise e

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Retrieves a job by its ID.

        :param job_id: The ID of the job to retrieve.
        :return: The job data if found, None otherwise.
        """
        return self.jobs.get(job_id, None)

    def get_outputs(self, job_id: str) -> Iterator[Any]:
        """
        Retrieves the outputs of a job by its ID.

        :param job_id: The ID of the job.
        :return: An iterator of job outputs.
        :raises ValueError: If the job is not found.
        """
        if job_id in self.jobs:
            return self.jobs.get(job_id).get_outputs()
        else:
            raise ValueError(f"Job with id {job_id} not found")

    def stop_outputs(self, job_id: str) -> None:
        """
        Stops the output stream of a job by its ID.

        :param job_id: The ID of the job.
        :raises ValueError: If the job is not found.
        """
        if job_id in self.jobs:
            return self.jobs.get(job_id).stop_outputs()
        else:
            raise ValueError(f"Job with id {job_id} not found")

    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """
        Updates the status of a job.

        :param job_id: The ID of the job to update.
        :param status: The new status of the job.
        :return: True if the job status was updated, False otherwise.
        """
        job = self.jobs.get(job_id)
        if job:
            job.status = status
            return True
        return False

    def delete_job(self, job_id: str) -> bool:
        """
        Deletes a job by its ID.

        :param job_id: The ID of the job to delete.
        :return: True if the job was deleted, False otherwise.
        """
        job = self.jobs.get(job_id, None)
        if job is None:
            return False
        if job.task.cancel() or job.task.done():
            job.stop_outputs()
            del self.jobs[job_id]
            return True
        return False

    def stop_all_jobs(self) -> None:
        """
        Stops all running jobs.
        """
        for job_id in list(self.jobs.keys()):
            self.delete_job(job_id)

    def shutdown(self, wait: bool = True) -> None:
        """
        Shuts down the job manager.

        :param wait: If True, wait for all jobs to complete before shutting down.
        """
        self.stop_all_jobs()
        self.executor.shutdown(wait=wait)
