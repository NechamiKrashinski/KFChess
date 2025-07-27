# pubsub.py (או הקובץ שבו נמצאים EventType ו-EventManager)

# pubsub.py

from enum import Enum
from typing import Callable, Any

class EventType(Enum):
    GAME_START = 1
    GAME_END = 2
    PIECE_MOVED = 3
    PIECE_CAPTURED = 4
    PIECE_JUMPED = 5

class EventManager:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: EventType, subscriber: Callable[[Any], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(subscriber)
        print(f"DEBUG: Listener registered for {event_type.name} (Value: {event_type.value}) - {subscriber.__name__}") # הוספה חשובה!
        
    def publish(self, event_type: EventType, *args, **kwargs):
        # print(f"DEBUG: Attempting to publish {event_type.name} (Value: {event_type.value}) with args: {args}, kwargs: {kwargs}") # הוספה נוספת לדיבוג פרסום
        if event_type in self.subscribers:
            for subscriber in self.subscribers[event_type]:
                try:
                    subscriber(*args, **kwargs)
                    # print(f"DEBUG: Successfully called listener {subscriber.__name__} for {event_type.name}") # הוספה לדיבוג קריאה
                except TypeError as e:
                    print(f"ERROR: Listener {subscriber.__name__} for {event_type.name} failed with arguments {args}, {kwargs}. Error: {e}. Expected signature: {inspect.signature(subscriber)}")
                except Exception as e:
                    print(f"ERROR: An unexpected error occurred in listener {subscriber.__name__} for {event_type.name}: {e}")
        else:
            print(f"DEBUG: No listeners registered for event type {event_type.name} (Value: {event_type.value})") # הוספה חשובה!