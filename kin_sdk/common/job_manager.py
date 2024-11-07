"""
Job Management System

This module provides a job management system with support for asynchronous job execution,
status tracking, and output streaming.
"""

import asyncio
import uuid
from enum import Enum
from typing import (
    Annotated,
    Any,
    AsyncGenerator,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
)

from pydantic import BaseModel, ConfigDict, Field

from kin_sdk.agent_module._module.base import BaseModule


class JobStatus(Enum):
    """
    Enumeration of possible job statuses.
    """

    UNKNOWN = 0
    STARTING = 1
    PROCESSING = 2
    CANCELED = 3
    FAILED = 4
    EXPIRED = 5
    SUCCESS = 6
    STOPPED = 7


class JobInfo(BaseModel):
    """
    Represents the status of a job.

    :param job_id: The ID of the job.
    :param job_status: The status of the job.
    """

    job_id: str
    job_status: JobStatus


class Job(BaseModel):
    """
    Represents a job with its associated data and methods.

    :param input_data: The input data for the job.
    :param setup_id: The setup ID associated with the job.
    :param instance_id: The setup instance ID associated with the job.
    :param module_ids: List of module IDs associated with the job.
    :param status: The current status of the job.
    :param function: The function to be executed as the job.
    :param output_queue: A queue to store job outputs.
    """

    id: str = Field(..., description="The ID of the job")
    model_config = ConfigDict(arbitrary_types_allowed=True)
    module: BaseModule = Field(..., description="The module associated with the job")
    input_data: BaseModel = Field(..., description="The input data for the job")
    setup_id: str = Field(..., description="The setup ID for the job")
    instance_id: str = Field(..., description="The setup instance ID for the job")
    module_ids: List[str] = Field(
        [], description="List of module IDs associated with the job"
    )
    status: JobStatus = Field(
        JobStatus.STARTING, description="The current status of the job"
    )
    function: Annotated[Callable[..., Any], Field(default_factory=Callable[..., Any])]
    output_queue: Annotated[asyncio.Queue, Field(default_factory=asyncio.Queue)]
    args: tuple = Field(..., description="Positional arguments for the job function")
    kwargs: dict = Field(..., description="Keyword arguments for the job function")

    def update_status(self, status: JobStatus) -> None:
        """
        Updates the status of the job.

        :param status: The new status of the job.
        """
        self.status = status


class JobManager:
    """
    Manages the lifecycle of jobs, including creation, retrieval, and termination.
    """

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.job_counter = 0

    async def start_job(
        self,
        module: BaseModule,
        input_data: BaseModel,
        setup_id: str,
        instance_id: str,
        module_ids: List[str],
        function: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """
        Creates and starts a new job with the given parameters.

        :param input_data: The input data for the job.
        :param setup_id: The setup ID for the job.
        :param instance_id: The instance ID associated with the job.
        :param module_ids: List of module IDs associated with the job.
        :param function: The function to be executed as the job.
        :param args: Positional arguments for the job function.
        :param kwargs: Keyword arguments for the job function.
        :return: The ID of the newly created job.
        """
        job_id = f"jobs:{uuid.uuid4().hex}"
        self.job_counter += 1
        output_queue = asyncio.Queue()
        job = Job(
            id=job_id,
            module=module,
            input_data=input_data,
            setup_id=setup_id,
            instance_id=instance_id,
            module_ids=module_ids,
            status=JobStatus.STARTING,
            function=function,
            output_queue=output_queue,
            args=args,
            kwargs=kwargs,
        )
        self.jobs[job_id] = job

        asyncio.create_task(self._run_job(job))
        return job_id

    async def _run_job(self, job: Job):
        """
        TODO: sphinx docstring
        """
        await job.function(job, *job.args, **job.kwargs)
        await job.output_queue.put(None)  # Indicate task completion
        try:
            await self.stop_job(job.id)  # Delete task after completion
        except ValueError:
            pass

    async def stop_job(self, job_id: str) -> Coroutine[Any, Any, None]:
        """
        Stop and delete a processing job.

        This method stop an async task associated to the job, update its status to STOPPED,
        and remove it from the job list.

        :param job_id: Unique ID of the job to stop.
        :type job_id: str
        :raises ValueError: If the job with the specified ID does not exist.
        :return: None
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job with id {job_id} does not exist")

        job = self.jobs[job_id]

        # retrieve the current task
        task = asyncio.current_task()
        if task:
            # cancel the task
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                # The task was successfully cancelled
                pass

        # Update the status of the job to STOPPED
        job.update_status(JobStatus.STOPPED)

        # Add a None element to the output queue to indicate the end of the output stream
        await job.output_queue.put(None)

        # Remove the job from the job list
        del self.jobs[job_id]
        self.job_counter -= 1

    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Retrieves a job by its ID.

        :param job_id: The ID of the job to retrieve.
        :return: The job data if found, None otherwise.
        """
        return self.jobs.get(job_id, None)

    async def output(self, job_id: str) -> AsyncGenerator[BaseModel, None]:
        """
        Générateur asynchrone pour lire les éléments de la file d'attente des outputs d'un job.

        :param job_id: L'ID du job.
        :yield: Les éléments de la file d'attente des outputs.
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job with id {job_id} does not exist")

        output_queue = self.jobs[job_id].output_queue
        while True:
            item = await output_queue.get()
            if item is None:
                print(" break " * 5)
                break
            yield item

    def update_status(self, job_id: str, status: JobStatus) -> bool:
        """
        Updates the status of a job.

        :param job_id: The ID of the job to update.
        :param status: The new status of the job.
        :return: True if the job status was updated, False otherwise.
        """
        job = self.get_job(job_id)
        if job:
            job.update_status(status)
            return True
        return False

    def get_jobs_list(self) -> List[JobInfo]:
        """
        Retrieves a list of ids and status of all jobs.

        :return: A dictionary containing the ids and status of all jobs.
        """
        return [
            JobInfo(job_id=job_id, job_status=job.status)
            for job_id, job in self.jobs.items()
        ]
