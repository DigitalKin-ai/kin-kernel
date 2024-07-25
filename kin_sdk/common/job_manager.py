"""
TODO sphinx docstring
"""

import uuid
import threading
from enum import Enum

from typing import Callable, Dict, List, Optional
from concurrent.futures import Future, ThreadPoolExecutor

from pydantic import BaseModel, ConfigDict


class JobStatus(Enum):
    STARTING = 0
    PROCESSING = 1
    CANCELED = 2
    FAILED = 3
    EXPIRED = 4
    SUCCESS = 5
    STOPPED = 6


class Job(BaseModel):
    """
    Represents a job.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    input_data: BaseModel
    setup_id: str
    service_ids: List[str]
    status: JobStatus
    task: Future


class JobManager:
    """
    Manages the lifecycle of jobs.
    """

    def __init__(self, max_workers: int = 10):
        self.jobs: Dict[str, Job] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()

    def start_job(
        self,
        input_data: BaseModel,
        setup_id: str,
        service_ids: List[str],
        func: Callable,
        *args,
        **kwargs,
    ) -> str:
        """
        Creates a new job with the given setup and service IDs.

        :param setup: The setup configuration for the job.
        :param service_ids: List of service IDs associated with the job.
        :return: The ID of the newly created job.
        """
        job_id = f"jobs:{uuid.uuid4().hex}"
        with self.lock:
            self.jobs[job_id] = Job(
                input_data=input_data,
                setup_id=setup_id,
                service_ids=service_ids,
                status=JobStatus.STARTING,
                task=self.executor.submit(func, job_id, *args, **kwargs),
            )
        return job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Retrieves a job by its ID.

        :param job_id: The ID of the job to retrieve.
        :return: The job data if found, None otherwise.
        """
        with self.lock:
            return self.jobs.get(job_id, None)

    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """
        Updates the status of a job.

        :param job_id: The ID of the job to update.
        :param status: The new status of the job.
        :return: True if the job status was updated, False otherwise.
        """
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].status = status
                return True
            return False

    def delete_job(self, job_id: str) -> bool:
        """
        Deletes a job by its ID.

        :param job_id: The ID of the job to delete.
        :return: True if the job was deleted, False otherwise.
        """
        with self.lock:
            job = self.jobs.get(job_id, None)
            if job is None:
                return False
            if job.task.cancel() or job.task.done():
                self.jobs.pop(job_id)
                return True
            return False

    def stop_all_jobs(self):
        """
        Stops all running jobs.
        """
        with self.lock:
            for job_id in list(self.jobs.keys()):
                self.delete_job(job_id)

    def shutdown(self, wait: bool = True):
        """
        Shuts down the job manager.
        """
        self.stop_all_jobs()
        self.executor.shutdown(wait=wait)
