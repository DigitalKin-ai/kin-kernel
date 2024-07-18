from collections import defaultdict
from typing import Callable, DefaultDict, List


class PubSub:
    def __init__(self):
        self.subscribers: DefaultDict[str, List[Callable[[str], None]]] = defaultdict(
            list
        )

    def subscribe(self, room: str, callback: Callable[[str], None]) -> None:
        self.subscribers[room].append(callback)

    def publish(self, user_name: str, room: str, message: str) -> None:
        for callback in self.subscribers[room]:
            print(f"publish to all subscriber of room: {room} message: {message}")
            callback(user_name, room, message)
