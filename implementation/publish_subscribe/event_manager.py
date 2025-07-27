# pubsub.py (או הקובץ שבו נמצאים EventType ו-EventManager)

# pubsub.py

from enum import Enum
from typing import Callable, Any

class EventType(Enum):
    GAME_START = 1
    GAME_END = 2
    PIECE_MOVED = 3
    PIECE_CAPTURED = 4

class EventManager:

    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: EventType, subscriber: Callable[[Any], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(subscriber)

    def publish(self, event_type: EventType, *args, **kwargs):
        if event_type in self.subscribers:
            for subscriber in self.subscribers[event_type]:
                subscriber(*args, **kwargs)

