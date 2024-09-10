"""TODO: Add a description here."""

import random
import asyncio
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel


class Task(BaseModel):
    """
    TODO: sphinx docstring
    """

    id: int
    function: Callable[..., Any]
    args: tuple
    kwargs: dict
    output_queue: asyncio.Queue

    class Config:
        """TODO"""

        arbitrary_types_allowed = True


class TaskManager:
    """
    TODO: sphinx docstring
    """

    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.task_counter = 0

    async def start_task(self, function: Callable[..., Any], *args, **kwargs) -> int:
        """
        TODO: sphinx docstring
        """
        self.task_counter += 1
        task_id = self.task_counter
        output_queue = asyncio.Queue()
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
        await task.function(task, *task.args, **task.kwargs)
        await task.output_queue.put(None)  # Indicate task completion
        await self.delete_task(task.id)  # Delete task after completion

    async def stop_task(self, task_id: int):
        """
        TODO: sphinx docstring
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.task_counter -= 1

    async def delete_task(self, task_id: int):
        """
        TODO: sphinx docstring
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.task_counter -= 1

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
            item = await output_queue.get()
            if item is None:
                break
            yield item


async def example_function(task: Task, *args, **kwargs):
    """
    TODO: sphinx docstring
    """
    # loop random size between 3 and 7
    for i in range(random.randint(3, 7)):
        await asyncio.sleep(1)
        await task.output_queue.put(
            f"Output {i} from task with args: {args}, kwargs: {kwargs}"
        )


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
    for i in range(3):
        if i == 1:
            task_id = await manager.start_task(example_function, 1, 2, 3)
        else:
            task_id = await manager.start_task(example_function, 1, 2, 3, key="value")
        print(f"Started task with id: {task_id}")
        task_ids.append(task_id)

    # Run task runners for each task
    await asyncio.gather(*(task_runner(manager, task_id) for task_id in task_ids))


# Run the main function
asyncio.run(main())
