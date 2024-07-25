"""
TODO sphinx docstring
"""

from queue import Queue
import uuid
import threading
from enum import Enum

from typing import Any, Callable, Dict, List, Optional
from concurrent.futures import Future, ThreadPoolExecutor

from pydantic import BaseModel, ConfigDict, Field


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
    outputs: Queue = Field(default_factory=Queue)
    stop_event: threading.Event = Field(default_factory=threading.Event)

    def add_to_outputs(self, item: Any):
        """
        Ajoute un élément à l'itérateur du job.
        """
        self.outputs.put(item)

    def stop_outputs(self):
        """
        Signale l'arrêt de l'itérateur.
        """
        self.stop_event.set()
        self.outputs.put(None)  # Sentinel value

    def get_outputs(self):
        """
        Retourne un itérateur pour les éléments du job.
        """
        while not self.stop_event.is_set():
            item = self.outputs.get()
            if item is None:  # Check for sentinel value
                break
            yield item


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
                outputs=Queue(),
                stop_event=threading.Event(),
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

    def get_outputs(self, job_id: str) -> Optional[Job]:
        """
        Retrieves the outputs of a job by its ID.
        """
        with self.lock:
            if job_id in self.jobs:
                return self.jobs.get(job_id).get_outputs()
            else:
                raise ValueError(f"Job with id {job_id} not found")

    def stop_outputs(self, job_id: str) -> Optional[Job]:
        """
        Retrieves the outputs of a job by its ID.
        """
        with self.lock:
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
                self.jobs.get(job_id).stop_outputs()
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
