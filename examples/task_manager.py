"""TODO: Add a description here."""

import random
import asyncio
from typing import Any, Callable, Dict, Optional
from queue import Queue
from pydantic import BaseModel


class Task(BaseModel):
    """
    TODO: sphinx docstring
    """

    id: int
    function: Callable[..., Any]
    args: tuple
    kwargs: dict
    output_queue: Queue

    class Config:
        """TODO"""

        arbitrary_types_allowed = True


class TaskManager:
    """
    TODO: sphinx docstring
    """

    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.loop = asyncio.get_event_loop()
        self.task_counter = 0

    async def start_task(self, function: Callable[..., Any], *args, **kwargs) -> int:
        """
        TODO: sphinx docstring
        """
        self.task_counter += 1
        task_id = self.task_counter
        output_queue = Queue()
        task = Task(
            id=task_id,
            function=function,
            args=args,
            kwargs=kwargs,
            output_queue=output_queue,
        )
        self.tasks[task_id] = task

        asyncio.create_task(self._run_task(task))
        return task_id

    async def _run_task(self, task: Task):
        """
        TODO: sphinx docstring
        """
        print(f"task.args: {task.args}")
        print(f"task.kwargs: {task.kwargs}")
        await task.function(task.output_queue)
        task.output_queue.put(None)  # Indicate task completion

    async def stop_task(self, task_id: int):
        """
        TODO: sphinx docstring
        """
        if task_id in self.tasks:
            del self.tasks[task_id]

    async def get_task(self, task_id: int) -> Optional[Task]:
        """
        TODO: sphinx docstring
        """
        return self.tasks.get(task_id)

    async def output(self, task_id: int):
        """
        TODO: sphinx docstring
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with id {task_id} does not exist")

        output_queue = self.tasks[task_id].output_queue
        while True:
            item = await self.loop.run_in_executor(None, output_queue.get)
            if item is None:
                break
            yield item


async def example_function(output_queue: Queue, *args, **kwargs):
    """
    TODO: sphinx docstring
    """
    # loop random size between 3 and 7
    for i in range(random.randint(3, 7)):
        await asyncio.sleep(1)
        output_queue.put(f"Output {i} from task with args: {args}, kwargs: {kwargs}")


async def task_runner(manager: TaskManager, task_id: int):
    """
    TODO: sphinx docstring
    """
    async for output in manager.output(task_id):
        print(f"Output from task {task_id}: {output}")


async def main():
    """
    TODO: sphinx docstring
    """
    manager = TaskManager()

    # Start three tasks
    task_ids = []
    for _ in range(3):
        task_id = await manager.start_task(example_function, 1, 2, 3, key="value")
        print(f"Started task with id: {task_id}")
        task_ids.append(task_id)

    # Run task runners for each task
    await asyncio.gather(*(task_runner(manager, task_id) for task_id in task_ids))


# Run the main function
asyncio.run(main())
